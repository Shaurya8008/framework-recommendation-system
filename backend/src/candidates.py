from typing import Any

def _get_val(obj: Any, attr: str, default: Any = "") -> Any:
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def generate_candidates(profile: Any, catalog: list[Any]) -> list[Any]:
    """
    Candidate generation step:
    Filters the full framework catalog into a shortlisted set of candidates
    applicable to the organization profile (high recall shortlist).
    """
    region = _get_val(profile, "region", "global")
    size = _get_val(profile, "size", "")

    shortlist = []
    for f in catalog:
        slug = _get_val(f, "slug", "")
        reg_app = _get_val(f, "region_applicability", ["global"]) or ["global"]

        # Regional filtering rules
        if "india" in reg_app and len(reg_app) == 1:
            # e.g. BRSR is primarily for India
            if region != "india":
                continue

        if slug == "csrd":
            # CSRD applies to EU or large companies
            if region != "eu" and size not in ["1000-5000", "5000+"]:
                continue

        shortlist.append(f)

    return shortlist
