"""
Exploratory Data Analysis (EDA) and Model Experiments for FrameworkFit.

This script demonstrates:
1. Loading the synthetic organization profiles dataset.
2. Exploring distribution of industries, sizes, regions, and emission maturity.
3. Analyzing feature correlation with recommended sustainability stages.
4. Experimenting with baseline vs XGBoost classifiers.
"""

import os
import pandas as pd
import numpy as np

def run_eda(data_path: str = "../data/synthetic_profiles.csv"):
    if not os.path.exists(data_path):
        from src.data_gen import generate_synthetic_profiles
        df = generate_synthetic_profiles(output_path=data_path)
    else:
        df = pd.read_csv(data_path)

    print("=" * 60)
    print("FRAMEWORKFIT — SYNTHETIC DATASET EDA")
    print("=" * 60)
    print(f"Total Profiles: {len(df)}")
    print("\nStage Distribution:")
    print(df["target_stage"].value_counts(normalize=True) * 100)
    print("\nTop 5 Recommended Frameworks:")
    print(df["target_framework_slug"].value_counts().head(5))
    print("\nEmissions Maturity vs Recommended Stage (crosstab):")
    print(pd.crosstab(df["emissions_maturity"], df["target_stage"], margins=True))
    print("=" * 60)
    return df

if __name__ == "__main__":
    run_eda()
