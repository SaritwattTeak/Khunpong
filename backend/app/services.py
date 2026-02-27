from __future__ import annotations
from datetime import datetime
from typing import List, Tuple

from sqlmodel import Session, select

from .constants import (
    STAR_SYSTEMS, TELESCOPE_LOCATIONS, FILE_TYPES, FILE_QUALITIES, IMAGE_MODES,
    CALIBRATION_UNITS, LIGHT_TYPES, FOLD_MIRROR_TYPES, DIRECTIONS
)
from .models import SciencePlan, StarSystem
from .data_schema import engine


def _get_star_system_name(star_system_id: int | None) -> str | None:
    """Resolve a StarSystem FK id back to its name string."""
    if star_system_id is None:
        return None
    with Session(engine) as session:
        star = session.get(StarSystem, star_system_id)
        return star.name if star else None


def validate_science_plan_fields(data: dict) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    required = [
    "creator", "submitter", "funding", "objective",
    "star_system_id",
    "schedule_start", "schedule_end",
    "telescope_location",
    "file_type", "file_quality",
    "image_mode", "exposure", "contrast", "brightness", "saturation"
    ]
    for k in required:
        if k not in data or data[k] in (None, "", []):
            errors.append(f"Missing required field: {k}")

    # typed/range checks
    obj = (data.get("objective") or "")
    if len(obj) > 500:
        errors.append("Objective must be <= 500 characters.")



    if data.get("telescope_location") and data["telescope_location"] not in TELESCOPE_LOCATIONS:
        errors.append("Telescope location must be Hawaii or Chile.")

    if data.get("file_type") and data["file_type"] not in FILE_TYPES:
        errors.append("File type must be PNG, JPEG, or RAW.")

    if data.get("file_quality") and data["file_quality"] not in FILE_QUALITIES:
        errors.append("File quality must be Low or Fine.")

    if data.get("image_mode") and data["image_mode"] not in IMAGE_MODES:
        errors.append("Image mode must be B&W or Color.")

    # schedule
    start = data.get("schedule_start")
    end = data.get("schedule_end")
    if isinstance(start, datetime) and isinstance(end, datetime):
        if start >= end:
            errors.append("Schedule start must be before schedule end.")

    # 0-50 constraints
    for k in ["exposure", "contrast", "brightness", "saturation"]:
        v = data.get(k)
        if v is None:
            continue
        try:
            iv = int(v)
            if iv < 0 or iv > 50:
                errors.append(f"{k.capitalize()} must be between 0 and 50.")
        except Exception:
            errors.append(f"{k.capitalize()} must be an integer.")

    # funding
    fund = data.get("funding")
    if fund is not None:
        try:
            float(fund)
        except Exception:
            errors.append("Funding must be a decimal number.")

    return (len(errors) == 0), errors


def run_virtual_telescope_validation(plan: SciencePlan) -> Tuple[bool, str]:
    data = plan.model_dump()

    ok, errors = validate_science_plan_fields(data)
    if not ok:
        return False, "Invalid: " + "; ".join(errors)

    return True, "Valid: Plan passed validation checks."


def validate_observing_program_fields(data: dict) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    required = [
        "calibration_unit", "light_type", "fold_mirror_type",
        "teleposition_degree", "teleposition_direction"
    ]
    for k in required:
        if k not in data or data[k] in (None, "", []):
            errors.append(f"Missing required field: {k}")

    if data.get("calibration_unit") and data["calibration_unit"] not in CALIBRATION_UNITS:
        errors.append("Calibration unit must be one of: Argon, CuAr, ThAr, Xenon.")

    if data.get("light_type") and data["light_type"] not in LIGHT_TYPES:
        errors.append("Light type must be CerroPachonSkyEmission or MaunaKeaSkyEmission.")

    if data.get("fold_mirror_type") and data["fold_mirror_type"] not in FOLD_MIRROR_TYPES:
        errors.append("Fold mirror type must be CASSEGRAIN_FOCUS or REFLECTIVE_CONVERGING_BEAM.")

    if data.get("teleposition_direction") and data["teleposition_direction"] not in DIRECTIONS:
        errors.append("Direction must be North, East, West, or South.")

    deg = data.get("teleposition_degree")
    if deg is not None:
        try:
            f = float(deg)
            if f < 0 or f > 360:
                errors.append("Teleposition degree must be between 0 and 360.")
        except Exception:
            errors.append("Teleposition degree must be a decimal number.")

    return (len(errors) == 0), errors