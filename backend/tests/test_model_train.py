import os
import shutil
import tempfile
from src.data_gen import generate_synthetic_profiles
from src.train import train_models


def test_train_models():
    with tempfile.TemporaryDirectory() as tmp_dir:
        data_path = os.path.join(tmp_dir, "test_profiles.csv")
        models_dir = os.path.join(tmp_dir, "test_models")

        # Generate small dataset for testing
        generate_synthetic_profiles(n_samples=50, output_path=data_path)

        clf, ranker = train_models(
            data_path=data_path,
            models_dir=models_dir,
            experiment_name="FrameworkFit-Test-Run"
        )

        assert clf is not None
        assert ranker is not None
        assert os.path.exists(os.path.join(models_dir, "v2_stage_classifier.joblib"))
        assert os.path.exists(os.path.join(models_dir, "v3_framework_ranker.joblib"))
