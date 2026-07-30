from src.data_gen import generate_synthetic_profiles


def test_generate_synthetic_profiles():
    df = generate_synthetic_profiles(n_samples=25, output_path=None)
    assert len(df) == 25
    assert "target_stage" in df.columns
    assert "target_framework_slug" in df.columns
    assert "target_score" in df.columns
    assert set(df["target_stage"].unique()).issubset({"manage", "measure", "report", "improve"})
