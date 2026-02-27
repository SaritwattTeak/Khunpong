from __future__ import annotations

from datetime import datetime
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from .data_schema import create_db_and_tables, get_session, seed_star_systems
from .models import SciencePlan, ValidationResult, ObservingProgram, StarSystem
from .constants import (
    STAR_SYSTEMS, TELESCOPE_LOCATIONS, FILE_TYPES, FILE_QUALITIES, IMAGE_MODES,
    CALIBRATION_UNITS, LIGHT_TYPES, FOLD_MIRROR_TYPES, DIRECTIONS
)
from .services import (
    validate_science_plan_fields, run_virtual_telescope_validation, validate_observing_program_fields
)

app = FastAPI(title="Gemini Project Prototype (UC-01..UC-03)")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_star_systems()  # ensure constellation rows exist


@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)):
    plans = session.exec(select(SciencePlan).order_by(SciencePlan.created_at.desc())).all()
    return templates.TemplateResponse("home.html", {"request": request, "plans": plans})


# ----------------------------
# UC-01 Create Science Plan
# ----------------------------

@app.get("/plans/new", response_class=HTMLResponse)
def new_plan(request: Request):
    return templates.TemplateResponse("plan_new.html", {
        "request": request,
        "STAR_SYSTEMS": STAR_SYSTEMS,
        "TELESCOPE_LOCATIONS": TELESCOPE_LOCATIONS,
        "FILE_TYPES": FILE_TYPES,
        "FILE_QUALITIES": FILE_QUALITIES,
        "IMAGE_MODES": IMAGE_MODES,
        "errors": [],
        "values": {}
    })


@app.post("/plans/new")
def create_plan(
    request: Request,
    session: Session = Depends(get_session),

    creator: str = Form(...),
    submitter: str = Form(...),
    funding: float = Form(...),
    objective: str = Form(...),

    star_system: str = Form(...),
    schedule_start: str = Form(...),
    schedule_end: str = Form(...),

    telescope_location: str = Form(...),

    file_type: str = Form(...),
    file_quality: str = Form(...),

    image_mode: str = Form(...),
    exposure: int = Form(...),
    contrast: int = Form(...),
    brightness: int = Form(...),
    saturation: int = Form(...),
):
    def parse_dt(s: str) -> datetime:
        return datetime.fromisoformat(s)

    errors = []

    # Resolve star system name → FK id
    star = session.exec(select(StarSystem).where(StarSystem.name == star_system)).first()
    if not star:
        errors.append(f"Star system '{star_system}' not found. Please select a valid option.")

    data = dict(
        creator=creator,
        submitter=submitter,
        funding=funding,
        objective=objective,
        star_system_id=star.id if star else None,
        schedule_start=parse_dt(schedule_start),
        schedule_end=parse_dt(schedule_end),
        telescope_location=telescope_location,
        file_type=file_type,
        file_quality=file_quality,
        image_mode=image_mode,
        exposure=exposure,
        contrast=contrast,
        brightness=brightness,
        saturation=saturation,
    )

    # Run field-level validation (your existing service)
    ok, field_errors = validate_science_plan_fields(data)
    if not ok:
        errors.extend(field_errors)

    if errors:
        return templates.TemplateResponse("plan_new.html", {
            "request": request,
            "STAR_SYSTEMS": STAR_SYSTEMS,
            "TELESCOPE_LOCATIONS": TELESCOPE_LOCATIONS,
            "FILE_TYPES": FILE_TYPES,
            "FILE_QUALITIES": FILE_QUALITIES,
            "IMAGE_MODES": IMAGE_MODES,
            "errors": errors,
            "values": {
                **data,
                "star_system": star_system,          # keep name for re-selecting dropdown
                "schedule_start": schedule_start,    # keep raw string for datetime-local input
                "schedule_end": schedule_end,
            }
        }, status_code=400)

    plan = SciencePlan(**data)
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return RedirectResponse(url=f"/plans/{plan.id}", status_code=303)


@app.get("/plans/{plan_id}", response_class=HTMLResponse)
def plan_detail(request: Request, plan_id: int, session: Session = Depends(get_session)):
    plan = session.get(SciencePlan, plan_id)
    if not plan:
        return HTMLResponse("Plan not found", status_code=404)

    results = session.exec(
        select(ValidationResult)
        .where(ValidationResult.plan_id == plan_id)
        .order_by(ValidationResult.created_at.desc())
    ).all()

    program = session.exec(
        select(ObservingProgram).where(ObservingProgram.plan_id == plan_id)
    ).first()

    return templates.TemplateResponse("plan_detail.html", {
        "request": request,
        "plan": plan,
        "results": results,
        "program": program
    })


# ----------------------------
# UC-02 Validate Science Plan
# ----------------------------

@app.post("/plans/{plan_id}/validate")
def validate_plan(plan_id: int, session: Session = Depends(get_session)):
    plan = session.get(SciencePlan, plan_id)
    if not plan:
        return HTMLResponse("Plan not found", status_code=404)

    is_valid, message = run_virtual_telescope_validation(plan)

    plan.status = "VALID" if is_valid else "INVALID"
    plan.updated_at = datetime.utcnow()

    vr = ValidationResult(plan_id=plan_id, is_valid=is_valid, message=message)
    session.add(vr)
    session.add(plan)
    session.commit()
    return RedirectResponse(url=f"/plans/{plan_id}", status_code=303)


# ----------------------------
# UC-03 Submit Observing Program
# ----------------------------

@app.get("/plans/{plan_id}/submit", response_class=HTMLResponse)
def submit_form(request: Request, plan_id: int, session: Session = Depends(get_session)):
    plan = session.get(SciencePlan, plan_id)
    if not plan:
        return HTMLResponse("Plan not found", status_code=404)

    if plan.status != "VALID":
        return templates.TemplateResponse(
            "submit_blocked.html", {"request": request, "plan": plan}, status_code=400
        )

    return templates.TemplateResponse("submit_form.html", {
        "request": request,
        "plan": plan,
        "CALIBRATION_UNITS": CALIBRATION_UNITS,
        "LIGHT_TYPES": LIGHT_TYPES,
        "FOLD_MIRROR_TYPES": FOLD_MIRROR_TYPES,
        "DIRECTIONS": DIRECTIONS,
        "errors": [],
        "values": {}
    })


@app.post("/plans/{plan_id}/submit")
def submit_program(
    request: Request,
    plan_id: int,
    session: Session = Depends(get_session),

    calibration_unit: str = Form(...),
    light_type: str = Form(...),
    fold_mirror_type: str = Form(...),
    teleposition_degree: float = Form(...),
    teleposition_direction: str = Form(...),
):
    plan = session.get(SciencePlan, plan_id)
    if not plan:
        return HTMLResponse("Plan not found", status_code=404)

    if plan.status != "VALID":
        return templates.TemplateResponse(
            "submit_blocked.html", {"request": request, "plan": plan}, status_code=400
        )

    data = dict(
        calibration_unit=calibration_unit,
        light_type=light_type,
        fold_mirror_type=fold_mirror_type,
        teleposition_degree=teleposition_degree,
        teleposition_direction=teleposition_direction,
    )

    ok, errors = validate_observing_program_fields(data)
    if not ok:
        return templates.TemplateResponse("submit_form.html", {
            "request": request,
            "plan": plan,
            "CALIBRATION_UNITS": CALIBRATION_UNITS,
            "LIGHT_TYPES": LIGHT_TYPES,
            "FOLD_MIRROR_TYPES": FOLD_MIRROR_TYPES,
            "DIRECTIONS": DIRECTIONS,
            "errors": errors,
            "values": data
        }, status_code=400)

    prog = ObservingProgram(plan_id=plan_id, **data, status="Pending Review")
    plan.status = "SUBMITTED"
    plan.updated_at = datetime.utcnow()

    session.add(prog)
    session.add(plan)
    session.commit()
    return RedirectResponse(url=f"/plans/{plan_id}", status_code=303)