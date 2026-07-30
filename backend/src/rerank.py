from typing import Any

STAGE_ORDER = ["manage", "measure", "report", "improve"]

# Prerequisite precedence within a stage (lower index = recommended first when scores are close)
PREREQ_PRECEDENCE = {
    "iso-14001": 1,
    "iso-50001": 2,
    "iso-45001": 3,
    "ghg-protocol": 1,
    "lca-iso-14040": 2,
    "iso-14064": 3,
    "csrd": 1,
    "brsr": 1,
    "issb": 2,
    "tcfd": 3,
    "gri": 4,
    "cdp": 5,
    "sbti": 1,
    "net-zero-standard": 2,
    "sdgs": 3,
    "renewable-energy-plan": 4,
}


def rerank_recommendations(scored_candidates: list[dict[str, Any]], profile: Any) -> dict[str, list[dict[str, Any]]]:
    """
    Re-ranking layer:
    1. Groups candidate frameworks into 4 stages: Manage -> Measure -> Report -> Improve
    2. Sorts candidates within each stage primarily by numeric score descending,
       and secondarily by prerequisite sequencing order.
    3. Guarantees business-logic order so foundational frameworks come first.
    """
    grouped: dict[str, list[dict[str, Any]]] = {
        "manage": [],
        "measure": [],
        "report": [],
        "improve": []
    }

    for item in scored_candidates:
        stage = item.get("stage", "manage")
        if stage not in grouped:
            grouped[stage] = []
        grouped[stage].append(item)

    # Sort within each stage by score descending, breaking ties with PREREQ_PRECEDENCE
    for stage_id in STAGE_ORDER:
        items = grouped[stage_id]
        items.sort(
            key=lambda x: (
                x.get("score", 0),
                -PREREQ_PRECEDENCE.get(x.get("slug", ""), 10)
            ),
            reverse=True
        )

    return grouped
