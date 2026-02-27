from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


# ---------------------------------------------------------------------------
# Lookup / reference table
# ---------------------------------------------------------------------------

class StarSystem(SQLModel, table=True):
    """Reference table populated from the 88 IAU constellations."""
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(unique=True, index=True)          # e.g. "Andromeda"
    meaning: str                                         # e.g. "Andromeda"
    area_sq_deg: float                                   # e.g. 722.278
    quadrant: str                                        # e.g. "NQ1"
    latitude_max: int                                    # e.g. 90
    latitude_min: int                                    # e.g. 40


# ---------------------------------------------------------------------------
# Core tables
# ---------------------------------------------------------------------------

class SciencePlan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # ── Data Description ────────────────────────────────────────────────────
    creator: str
    submitter: str
    funding: float
    objective: str = Field(max_length=500)

    # ── Star System (FK to lookup table) ────────────────────────────────────
    star_system_id: int = Field(foreign_key="starsystem.id")

    # ── Schedule ────────────────────────────────────────────────────────────
    schedule_start: datetime
    schedule_end: datetime

    # ── Telescope ───────────────────────────────────────────────────────────
    telescope_location: str   # "Hawaii" | "Chile"

    # ── Data Processing Requirements ────────────────────────────────────────
    file_type: str            # "PNG" | "JPEG" | "RAW"
    file_quality: str         # "Low" | "Fine"

    # ── Image Processing ────────────────────────────────────────────────────
    image_mode: str           # "B&W" | "Color"
    exposure: int             # 0–50
    contrast: int             # 0–50
    brightness: int           # 0–50
    saturation: int           # 0–50

    # ── Workflow status ─────────────────────────────────────────────────────
    status: str = Field(default="DRAFT")   # DRAFT | VALID | INVALID | SUBMITTED

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ValidationResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="scienceplan.id")

    is_valid: bool
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ObservingProgram(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="scienceplan.id")

    # ── Observing Program fields ─────────────────────────────────────────────
    calibration_unit: str        # "Argon" | "CuAr" | "ThAr" | "Xenon"
    light_type: str              # "CerroPachonSkyEmission" | "MaunaKeaSkyEmission"
    fold_mirror_type: str        # "CASSEGRAIN_FOCUS" | "REFLECTIVE_CONVERGING_BEAM"
    teleposition_degree: float   # 0–360
    teleposition_direction: str  # "North" | "East" | "West" | "South"

    status: str = Field(default="Pending Review")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)