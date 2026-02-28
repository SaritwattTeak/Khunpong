from __future__ import annotations
from datetime import datetime
from typing import List, Tuple

from .constants import (
    TELESCOPE_LOCATIONS,
    FILE_TYPES,
    FILE_QUALITIES,
    IMAGE_MODES,
    CALIBRATION_UNITS,
    LIGHT_TYPES,
    FOLD_MIRROR_TYPES,
    DIRECTIONS,
)
from .models import SciencePlan


# ============================================================
# CORE FIELD VALIDATION (Used by both Astronomer & Observer)
# ============================================================

def validate_science_plan_fields(data: dict) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    required = [
        "creator", "submitter", "funding", "objective",
        "star_system_id",
        "schedule_start", "schedule_end",
        "telescope_location",
        "file_type", "file_quality",
        "image_mode", "exposure", "contrast",
        "brightness", "saturation"
    ]

    for field in required:
        if field not in data or data[field] in (None, "", []):
            errors.append(f"Missing required field: {field}")

    # Objective length
    if len(data.get("objective", "")) > 500:
        errors.append("Objective must be <= 500 characters.")

    # Telescope location
    if data.get("telescope_location") not in TELESCOPE_LOCATIONS:
        errors.append("Invalid telescope location.")

    # File settings
    if data.get("file_type") not in FILE_TYPES:
        errors.append("Invalid file type.")

    if data.get("file_quality") not in FILE_QUALITIES:
        errors.append("Invalid file quality.")

    if data.get("image_mode") not in IMAGE_MODES:
        errors.append("Invalid image mode.")

    # Schedule validation
    start = data.get("schedule_start")
    end = data.get("schedule_end")

    if isinstance(start, datetime) and isinstance(end, datetime):
        if start >= end:
            errors.append("Schedule start must be before schedule end.")
    else:
        errors.append("Invalid schedule format.")

    # Numeric range validation (0–50)
    for field in ["exposure", "contrast", "brightness", "saturation"]:
        try:
            value = int(data.get(field))
            if value < 0 or value > 50:
                errors.append(f"{field.capitalize()} must be between 0 and 50.")
        except Exception:
            errors.append(f"{field.capitalize()} must be an integer.")

    # Funding numeric check
    try:
        float(data.get("funding"))
    except Exception:
        errors.append("Funding must be a decimal number.")

    return len(errors) == 0, errors


# ============================================================
# ASTRONOMER: VIRTUAL TELESCOPE SIMULATION
# (No status change. No approval authority.)
# ============================================================

def run_virtual_telescope_test(plan: SciencePlan) -> Tuple[bool, List[str]]:
    """
    Astronomer simulation mode.
    Returns technical feedback only.
    Does NOT approve or reject.
    """

    feedback: List[str] = []
    data = plan.model_dump()

    # Basic structural validation
    ok, errors = validate_science_plan_fields(data)
    if not ok:
        feedback.extend(errors)

    # --------------------------------------------------------
    # Simulated Telescope Constraints
    # --------------------------------------------------------

    # Exposure warning
    if plan.exposure > 40 and plan.image_mode == "Color":
        feedback.append(
            "Warning: High exposure with Color mode may cause sensor saturation."
        )

    # Brightness / contrast interaction
    if plan.brightness < 5 and plan.contrast < 5:
        feedback.append(
            "Warning: Very low brightness and contrast may reduce image clarity."
        )

    # Long observation duration
    duration_hours = (
        (plan.schedule_end - plan.schedule_start).total_seconds() / 3600
    )

    if duration_hours > 12:
        feedback.append(
            "Warning: Observation window exceeds 12 hours. Telescope allocation may be restricted."
        )

    # Low funding soft warning
    if plan.funding < 1000:
        feedback.append(
            "Warning: Funding below recommended operational threshold."
        )

    if not feedback:
        feedback.append("Simulation successful. No technical issues detected.")

    return True, feedback


# ============================================================
# OBSERVER: OFFICIAL VALIDATION
# (Authority decision)
# ============================================================

def run_official_validation(plan: SciencePlan) -> Tuple[bool, List[str]]:
    """
    Science Observer official validation.
    Determines approval or rejection.
    """

    ok, errors = validate_science_plan_fields(plan.model_dump())

    if not ok:
        return False, errors

    # Strict rule example:
    if plan.exposure > 45:
        return False, ["Exposure exceeds maximum allowed operational limit (45)."]

    if plan.funding < 500:
        return False, ["Funding below minimum requirement for approval."]

    return True, ["Plan meets all validation criteria."]


# ============================================================
# OBSERVING PROGRAM VALIDATION
# ============================================================

def validate_observing_program_fields(data: dict) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    required = [
        "calibration_unit",
        "light_type",
        "fold_mirror_type",
        "teleposition_degree",
        "teleposition_direction"
    ]

    for field in required:
        if field not in data or data[field] in (None, "", []):
            errors.append(f"Missing required field: {field}")

    if data.get("calibration_unit") not in CALIBRATION_UNITS:
        errors.append("Invalid calibration unit.")

    if data.get("light_type") not in LIGHT_TYPES:
        errors.append("Invalid light type.")

    if data.get("fold_mirror_type") not in FOLD_MIRROR_TYPES:
        errors.append("Invalid fold mirror type.")

    if data.get("teleposition_direction") not in DIRECTIONS:
        errors.append("Invalid teleposition direction.")

    try:
        degree = float(data.get("teleposition_degree"))
        if degree < 0 or degree > 360:
            errors.append("Teleposition degree must be between 0 and 360.")
    except Exception:
        errors.append("Teleposition degree must be numeric.")

    return len(errors) == 0, errors