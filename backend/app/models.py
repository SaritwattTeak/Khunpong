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

    name: str = Field(unique=True, index=True)
    meaning: str
    area_sq_deg: float
    quadrant: str
    latitude_max: int
    latitude_min: int


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
    telescope_location: str

    # ── Data Processing Requirements ────────────────────────────────────────
    file_type: str
    file_quality: str

    # ── Image Processing ────────────────────────────────────────────────────
    image_mode: str
    exposure: int
    contrast: int
    brightness: int
    saturation: int

    # ── Workflow status ─────────────────────────────────────────────────────
    status: str = Field(default="DRAFT")   # DRAFT | SUBMITTED

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ValidationResult(SQLModel, table=True):
    """
    Stores simulation feedback messages only.
    No approval logic here.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="scienceplan.id")

    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ObservingProgram(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="scienceplan.id")

    calibration_unit: str
    light_type: str
    fold_mirror_type: str
    teleposition_degree: float
    teleposition_direction: str

    status: str = Field(default="Pending Review")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)