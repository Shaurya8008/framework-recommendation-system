import os
import joblib
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error
from src.features import extract_features_dataframe
from src.data_gen import generate_synthetic_profiles
from app.db.seed import INITIAL_FRAMEWORKS


def compute_top_k_accuracy(y_true: np.ndarray, probs: np.ndarray, classes: np.ndarray, k: int = 2) -> float:
    """
    Computes top-k accuracy for stage classification.
    """
    correct = 0
    for true_label, prob_row in zip(y_true, probs):
        top_k_idx = np.argsort(prob_row)[::-1][:k]
        top_k_classes = [classes[idx] for idx in top_k_idx]
        if true_label in top_k_classes:
            correct += 1
    return float(correct / len(y_true))


def compute_ranking_metrics_at_k(profiles_df: pd.DataFrame, ranker: RandomForestRegressor, classifier: RandomForestClassifier, k: int = 3) -> dict[str, float]:
    """
    Computes precision@k and recall@k for framework recommendations across the evaluation set.
    """
    precisions = []
    recalls = []

    for _, row in profiles_df.iterrows():
        true_framework = row["target_framework_slug"]
        profile_dict = row.to_dict()
        c_val = row.get("certifications_str", "")
        profile_dict["certifications"] = str(c_val).split(",") if pd.notna(c_val) and str(c_val) else []
        g_val = row.get("goals_str", "")
        profile_dict["goals"] = str(g_val).split(",") if pd.notna(g_val) and str(g_val) else []

        f_df = extract_features_dataframe([profile_dict])
        stage_probs = classifier.predict_proba(f_df)[0]
        prob_map = {cls: float(prob) for cls, prob in zip(classifier.classes_, stage_probs)}

        scored_list = []
        for f in INITIAL_FRAMEWORKS:
            slug = f["slug"]
            stage = f["stage"]
            stage_mult = prob_map.get(stage, 0.25) * 4.0

            f_row = f_df.copy()
            f_row["framework_slug_hash"] = hash(slug) % 1000
            base_score = float(ranker.predict(f_row)[0])
            score = base_score * (0.8 + 0.2 * stage_mult)
            scored_list.append((slug, score))

        scored_list.sort(key=lambda x: x[1], reverse=True)
        top_k_slugs = [slug for slug, _ in scored_list[:k]]

        # Since synthetic data has 1 primary target framework, recall is 1.0 if found else 0.0
        hit = int(true_framework in top_k_slugs)
        recalls.append(hit)
        precisions.append(hit / float(k))

    return {
        f"precision_at_{k}": float(np.mean(precisions)),
        f"recall_at_{k}": float(np.mean(recalls)),
    }


def train_models(data_path: str = "data/synthetic_profiles.csv", models_dir: str = "models", experiment_name: str = "FrameworkFit-Recommendation-Pipeline"):
    """
    Trains v2 Stage Classifier and v3 Framework Ranker, logs experiment parameters
    and metrics to MLflow, and saves model artifacts to models_dir.
    """
    os.makedirs(models_dir, exist_ok=True)

    # Ensure dataset exists
    if not os.path.exists(data_path):
        df = generate_synthetic_profiles(output_path=data_path)
    else:
        df = pd.read_csv(data_path)

    # Prepare features
    profiles_list = []
    for _, row in df.iterrows():
        p = row.to_dict()
        p["certifications"] = [c for c in str(p.get("certifications_str", "")).split(",") if c]
        p["goals"] = [g for g in str(p.get("goals_str", "")).split(",") if g]
        profiles_list.append(p)

    X = extract_features_dataframe(profiles_list)
    y_stage = df["target_stage"].values
    y_score = df["target_score"].values

    # Train/Test Split
    X_train, X_test, y_stage_train, y_stage_test, y_score_train, y_score_test, df_train, df_test = train_test_split(
        X, y_stage, y_score, df, test_size=0.2, random_state=42
    )

    mlflow.set_tracking_uri("sqlite:///mlruns.db")
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name="v2_classifier_and_v3_ranker"):
        # Log dataset parameters
        mlflow.log_param("n_samples", len(df))
        mlflow.log_param("test_size", 0.2)
        mlflow.log_param("classifier_type", "RandomForestClassifier")
        mlflow.log_param("ranker_type", "RandomForestRegressor")

        # 1. Train v2 Stage Classifier
        v2_classifier = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        v2_classifier.fit(X_train, y_stage_train)

        stage_preds = v2_classifier.predict(X_test)
        stage_probs = v2_classifier.predict_proba(X_test)
        acc = accuracy_score(y_stage_test, stage_preds)
        top_2_acc = compute_top_k_accuracy(y_stage_test, stage_probs, v2_classifier.classes_, k=2)

        mlflow.log_metric("v2_stage_accuracy", acc)
        mlflow.log_metric("v2_top_2_accuracy", top_2_acc)
        print(f"v2 Stage Classifier - Accuracy: {acc:.4f}, Top-2 Accuracy: {top_2_acc:.4f}")

        # 2. Train v3 Framework Ranker
        X_train_ranker = X_train.copy()
        X_train_ranker["framework_slug_hash"] = [hash(s) % 1000 for s in df_train["target_framework_slug"]]
        X_test_ranker = X_test.copy()
        X_test_ranker["framework_slug_hash"] = [hash(s) % 1000 for s in df_test["target_framework_slug"]]

        v3_ranker = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        v3_ranker.fit(X_train_ranker, y_score_train)

        score_preds = v3_ranker.predict(X_test_ranker)
        rmse = float(np.sqrt(mean_squared_error(y_score_test, score_preds)))
        mlflow.log_metric("v3_ranker_rmse", rmse)
        print(f"v3 Framework Ranker - RMSE: {rmse:.4f}")

        # 3. Compute precision@k and recall@k for framework recommendations
        metrics_k = compute_ranking_metrics_at_k(df_test, v3_ranker, v2_classifier, k=3)
        for metric_name, val in metrics_k.items():
            mlflow.log_metric(metric_name, val)
            print(f"{metric_name}: {val:.4f}")

        # 4. Save model artifacts
        v2_path = os.path.join(models_dir, "v2_stage_classifier.joblib")
        v3_path = os.path.join(models_dir, "v3_framework_ranker.joblib")
        joblib.dump(v2_classifier, v2_path)
        joblib.dump(v3_ranker, v3_path)

        mlflow.log_artifact(v2_path, artifact_path="models")
        mlflow.log_artifact(v3_path, artifact_path="models")

        print(f"Saved trained models to {v2_path} and {v3_path}")
        return v2_classifier, v3_ranker


if __name__ == "__main__":
    train_models()
