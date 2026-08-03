from src.pipeline import RecommendationPipeline
from app.db.seed import INITIAL_FRAMEWORKS


def test_recommendation_pipeline_no_emissions(sample_profile_dict):
    sample_profile_dict["emissions_maturity"] = "none"
    pipeline = RecommendationPipeline(models_dir="nonexistent_dir")  # tests v1 fallback
    result = pipeline.recommend(sample_profile_dict)

    assert "profileSummary" in result
    assert "stages" in result
    stages = result["stages"]
    assert set(stages.keys()) == {"manage", "measure", "report", "improve"}

    # Check measure stage includes ghg-protocol with high score
    measure_slugs = [item["slug"] for item in stages["measure"]]
    assert "ghg-protocol-corporate" in measure_slugs

    # Verify each recommendation item structure
    for stage_items in stages.values():
        for item in stage_items:
            assert "slug" in item
            assert "name" in item
            assert "stage" in item
            assert "description" in item
            assert "score" in item
            assert "reason" in item
            assert 0 <= item["score"] <= 100
