from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class SciencePlan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Data specification fields
    creator: str
    submitter: str
    funding: float
    objective: str = Field(max_length=500)

    star_system: str
    schedule_start: datetime
    schedule_end: datetime

    telescope_location: str  # Hawaii or Chile

    file_type: str           # PNG, JPEG, RAW
    file_quality: str        # Low, Fine

    image_mode: str          # B&W, Color
    exposure: int            # 0-50
    contrast: int            # 0-50
    brightness: int          # 0-50
    saturation: int          # 0-50

    # status for UC-02 / UC-03
    status: str = Field(default="DRAFT")  # DRAFT, VALID, INVALID, SUBMITTED

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

    # Data specification fields (Observing Program section)
    calibration_unit: str
    light_type: str
    fold_mirror_type: str
    teleposition_degree: float  # 0-360
    teleposition_direction: str # North/East/West/South

    status: str = Field(default="Pending Review")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
