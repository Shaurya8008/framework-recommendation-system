"""
Business re-ranking module.

Applies business logic re-ranking after raw scores are computed:
1. Respect foundational sequencing: Manage → Measure → Report → Improve
2. Ensure management frameworks stay near top when none exist
3. GHG Protocol must outrank SBTi when no emissions inventory exists
4. Mandatory regional disclosures outrank voluntary
5. Deduplicate near-identical frameworks crowding top results
6. Preserve diversity across stages
"""

from __future__ import annotations
from typing import Any

from src.normalize_profile import NormalizedProfile


STAGE_ORDER = ["manage", "measure", "report", "improve"]

# Foundational precedence within stages (lower = recommended first when close)
STAGE_PRECEDENCE: dict[str, int] = {
    # Manage
    "iso-14001": 1,
    "iso-50001": 2,
    "iso-45001": 3,
    "iso-46001": 4,
    "sa8000": 5,
    "iso-20400": 6,
    "iso-37001": 7,
    "aws-standard": 8,
    # Measure
    "ghg-protocol-corporate": 1,
    "ghg-protocol-scope2": 2,
    "ghg-protocol-scope3": 3,
    "iso-14064-1": 4,
    "iso-14064-2": 5,
    "iso-14067": 6,
    "iso-14040": 7,
    "iso-14044": 8,
    "iso-14046": 9,
    "pcaf": 4,
    "water-footprint": 10,
    # Report
    "brsr": 1,
    "brsr-core": 2,
    "csrd": 1,
    "esrs": 2,
    "ifrs-s1": 3,
    "ifrs-s2": 4,
    "gri": 5,
    "tcfd": 6,
    "sasb": 7,
    "cdp-climate": 8,
    "cdp-water": 9,
    "ecovadis": 10,
    "integrated-reporting": 11,
    "ungc-cop": 12,
    # Improve
    "sbti": 1,
    "net-zero-standard": 2,
    "re100": 3,
    "ep100": 4,
    "ev100": 5,
    "race-to-zero": 6,
    "sdgs": 7,
    "circulytics": 8,
    "true-zero-waste": 9,
}

# Near-duplicate groups — only keep the highest-scored from each group in top results
DUPLICATE_GROUPS = [
    {"brsr", "brsr-core"},
    {"csrd", "esrs"},
    {"ifrs-s1", "ifrs-s2"},
    {"iso-14040", "iso-14044"},
    {"iso-14064-1", "iso-14064-2"},
    {"ghg-protocol-scope2", "ghg-protocol-scope3"},
    {"cdp-climate", "cdp-water"},
]


def _group_by_stage(scored: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group scored candidates into stage buckets."""
    grouped: dict[str, list[dict[str, Any]]] = {s: [] for s in STAGE_ORDER}
    for item in scored:
        stage = item.get("stage", "manage")
        if stage not in grouped:
            grouped[stage] = []
        grouped[stage].append(item)
    return grouped


def _sort_within_stage(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort by score descending, break ties with precedence."""
    items.sort(
        key=lambda x: (
            x.get("score", 0),
            -STAGE_PRECEDENCE.get(x.get("slug", ""), 50),
        ),
        reverse=True,
    )
    return items


def _apply_foundation_rules(
    grouped: dict[str, list[dict[str, Any]]],
    profile: NormalizedProfile,
) -> dict[str, list[dict[str, Any]]]:
    """
    Apply business rules that override raw scoring:
    1. If no management certs exist, ensure a MANAGE framework is near top
    2. If no emissions inventory, GHG Protocol must outrank advanced targets
    """
    certs = set(profile.existing_certifications)

    # Rule 1: If no EMS cert, boost ISO 14001 within manage
    if not certs & {"iso-14001", "iso-50001", "iso-45001"}:
        manage_items = grouped.get("manage", [])
        for item in manage_items:
            if item["slug"] == "iso-14001":
                item["score"] = max(item["score"], 85.0)
                break

    # Rule 2: If no emissions inventory, suppress advanced targets
    if profile.emissions_tracking_maturity == "none":
        # Boost GHG Protocol in measure
        for item in grouped.get("measure", []):
            if item["slug"] == "ghg-protocol-corporate":
                item["score"] = max(item["score"], 90.0)
                break

        # Suppress SBTi and Net Zero in improve
        for item in grouped.get("improve", []):
            if item["slug"] in ("sbti", "net-zero-standard"):
                # Cap but don't completely remove
                item["score"] = min(item["score"], 55.0)

    # Rule 3: Mandatory regional disclosures outrank voluntary
    report_items = grouped.get("report", [])
    for item in report_items:
        if item.get("mandatory_status") == "mandatory":
            # Ensure mandatory frameworks score at least 75
            item["score"] = max(item["score"], 75.0)

    return grouped


def _deduplicate_top_results(
    grouped: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    """
    Prevent near-duplicate frameworks from crowding the top of each stage.
    Within each duplicate group, only the highest-scored keeps its rank;
    others get a small penalty.
    """
    for stage in STAGE_ORDER:
        items = grouped.get(stage, [])
        for dup_group in DUPLICATE_GROUPS:
            group_items = [i for i in items if i["slug"] in dup_group]
            if len(group_items) > 1:
                # Sort within group, penalise all but the best
                group_items.sort(key=lambda x: x["score"], reverse=True)
                for secondary in group_items[1:]:
                    secondary["score"] = max(0, secondary["score"] - 3.0)
    return grouped


def rerank(
    scored_candidates: list[dict[str, Any]],
    profile: NormalizedProfile,
) -> dict[str, list[dict[str, Any]]]:
    """
    Full re-ranking pipeline:
    1. Group by stage
    2. Apply foundation rules
    3. Deduplicate
    4. Sort within each stage
    5. Return ordered groups
    """
    grouped = _group_by_stage(scored_candidates)
    grouped = _apply_foundation_rules(grouped, profile)
    grouped = _deduplicate_top_results(grouped)

    # Final sort within each stage
    for stage in STAGE_ORDER:
        grouped[stage] = _sort_within_stage(grouped.get(stage, []))

    return grouped
