import os
import random
import pandas as pd
import numpy as np
from src.features import (
    INDUSTRIES, SIZES, REGIONS, ENERGY_LEVELS, MATURITIES, DISCLOSURES,
    CERT_SLUGS, GOAL_SLUGS, compute_domain_scores
)
from src.model import RuleBasedScorer
from app.db.seed import INITIAL_FRAMEWORKS


def generate_synthetic_profiles(n_samples: int = 600, seed: int = 42, output_path: str = "data/synthetic_profiles.csv") -> pd.DataFrame:
    """
    Generates a synthetic labeled dataset of organization profiles and their true
    recommended stage and top framework, for bootstrap ML model training.
    """
    random.seed(seed)
    np.random.seed(seed)

    rows = []
    for i in range(n_samples):
        ind = random.choice(INDUSTRIES)
        size = random.choice(SIZES)
        reg = random.choice(REGIONS)
        energy = random.choice(ENERGY_LEVELS)
        mat = random.choice(MATURITIES)
        disc = random.choice(DISCLOSURES)

        # Generate realistic certification subsets
        n_certs = random.choice([0, 0, 1, 1, 2, 3])
        certs = random.sample(CERT_SLUGS, min(n_certs, len(CERT_SLUGS)))

        # Generate realistic goal subsets
        n_goals = random.choice([0, 1, 1, 2, 3])
        goals = random.sample(GOAL_SLUGS, min(n_goals, len(GOAL_SLUGS)))

        profile = {
            "organization_name": f"Synthetic Org #{i+1}",
            "industry": ind,
            "size": size,
            "region": reg,
            "energy_use_level": energy,
            "emissions_maturity": mat,
            "certifications": certs,
            "disclosure_level": disc,
            "goals": goals,
        }

        # Use domain rules to determine the true recommended stage and framework
        # If no emissions inventory -> measure stage is top priority
        # If no EMS -> manage stage is top priority
        # If EU/India or full disclosure -> report stage has high urgency
        # If net-zero/sbti goal -> improve stage is key
        best_score = -1
        best_framework = "iso-14001"
        best_stage = "manage"

        for f in INITIAL_FRAMEWORKS:
            score, _ = RuleBasedScorer.score(profile, f)
            # Add small random noise to simulate real-world variance
            noisy_score = score + np.random.normal(0, 3)
            if noisy_score > best_score:
                best_score = noisy_score
                best_framework = f["slug"]
                best_stage = f["stage"]

        row = {
            **profile,
            "certifications_str": ",".join(certs),
            "goals_str": ",".join(goals),
            "target_stage": best_stage,
            "target_framework_slug": best_framework,
            "target_score": int(np.clip(round(best_score), 10, 99))
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Generated {len(df)} synthetic profiles -> {output_path}")

    return df


if __name__ == "__main__":
    generate_synthetic_profiles()
