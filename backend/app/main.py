from __future__ import annotations
from datetime import datetime

from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from sqlmodel import Session, select
from passlib.context import CryptContext

from .data_schema import create_db_and_tables, get_session, seed_star_systems, engine
from .models import (
    SciencePlan,
    ValidationResult,
    ObservingProgram,
    StarSystem,
)
from .user_schema import User
from .constants import (
    STAR_SYSTEMS,
    TELESCOPE_LOCATIONS,
    FILE_TYPES,
    FILE_QUALITIES,
    IMAGE_MODES,
    CALIBRATION_UNITS,
    LIGHT_TYPES,
    FOLD_MIRROR_TYPES,
    DIRECTIONS,
)
from .services import (
    validate_science_plan_fields,
    run_virtual_telescope_test,
    run_official_validation,
    validate_observing_program_fields,
)

# ============================================================
# App Setup
# ============================================================

app = FastAPI(title="Gemini Project Prototype (Simulation Version)")

templates = Jinja2Templates(directory="app/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def resolve_star_system(plan: SciencePlan, session: Session) -> dict:
    """Return plan as a dict with star_system name resolved (Jinja2 dot-notation works on dicts)."""
    star = session.get(StarSystem, plan.star_system_id)
    d = plan.model_dump()
    d["star_system"] = star.name if star else "Unknown"
    return d

# ============================================================
# Password Utilities
# ============================================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ============================================================
# Authentication Helpers
# ============================================================

def get_current_user(
    request: Request,
    session: Session = Depends(get_session)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return session.get(User, user_id)

def require_role(role: str):
    def checker(
        request: Request,
        session: Session = Depends(get_session)
    ):
        user_id = request.session.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Not logged in")

        user = session.get(User, user_id)

        if not user or user.role != role:
            raise HTTPException(status_code=403, detail="Forbidden")

        return user

    return checker

# ============================================================
# Global Auth Middleware
# ============================================================

@app.middleware("http")
async def auth_middleware(request: Request, call_next):

    public_paths = ["/login", "/static"]

    if not any(request.url.path.startswith(p) for p in public_paths):
        if not request.session.get("user_id"):
            return RedirectResponse("/login", status_code=303)

    return await call_next(request)

# SessionMiddleware must be added AFTER auth_middleware so it runs outermost first
app.add_middleware(
    SessionMiddleware,
    secret_key="SUPER_SECRET_KEY_CHANGE_THIS"
)

# ============================================================
# Startup
# ============================================================

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_star_systems()

    with Session(engine) as session:
        for username, password, role in [
            ("astro",    "astro123",    "Astronomer"),
            ("observer", "observer123", "ScienceObserver"),
            ("operator", "operator123", "TelescopeOperator"),
        ]:
            if not session.exec(select(User).where(User.username == username)).first():
                session.add(User(
                    username=username,
                    password_hash=hash_password(password),
                    role=role,
                ))
        session.commit()

# ============================================================
# Login / Logout
# ============================================================

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None}
    )

@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    user = session.exec(
        select(User).where(User.username == username)
    ).first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password"}
        )

    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)

# ============================================================
# Home
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    plans_orm = session.exec(
        select(SciencePlan).order_by(SciencePlan.created_at.desc())
    ).all()
    plans = [resolve_star_system(p, session) for p in plans_orm]

    return templates.TemplateResponse(
        "home.html",
        {"request": request, "plans": plans, "user": user}
    )

# ============================================================
# Create Science Plan (Astronomer Only)
# ============================================================

@app.get("/plans/new", response_class=HTMLResponse)
def new_plan(
    request: Request,
    user: User = Depends(require_role("Astronomer"))
):
    return templates.TemplateResponse(
        "plan_new.html",
        {
            "request": request,
            "STAR_SYSTEMS": STAR_SYSTEMS,
            "TELESCOPE_LOCATIONS": TELESCOPE_LOCATIONS,
            "FILE_TYPES": FILE_TYPES,
            "FILE_QUALITIES": FILE_QUALITIES,
            "IMAGE_MODES": IMAGE_MODES,
            "errors": [],
            "values": {},
            "user": user
        }
    )

@app.post("/plans/new")
def create_plan(
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_role("Astronomer")),

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

    star = session.exec(
        select(StarSystem).where(StarSystem.name == star_system)
    ).first()

    if not star:
        errors.append("Invalid star system selected.")

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

    ok, field_errors = validate_science_plan_fields(data)
    if not ok:
        errors.extend(field_errors)

    if errors:
        return templates.TemplateResponse(
            "plan_new.html",
            {
                "request": request,
                "STAR_SYSTEMS": STAR_SYSTEMS,
                "TELESCOPE_LOCATIONS": TELESCOPE_LOCATIONS,
                "FILE_TYPES": FILE_TYPES,
                "FILE_QUALITIES": FILE_QUALITIES,
                "IMAGE_MODES": IMAGE_MODES,
                "errors": errors,
                "values": data,
                "user": user
            },
            status_code=400
        )

    plan = SciencePlan(**data, status="DRAFT")

    session.add(plan)
    session.commit()
    session.refresh(plan)

    return RedirectResponse(f"/plans/{plan.id}", status_code=303)

# ============================================================
# Plan Detail (GET /plans/{plan_id})
# ============================================================

@app.get("/plans/{plan_id}", response_class=HTMLResponse)
def plan_detail(
    plan_id: int,
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    plan_orm = session.get(SciencePlan, plan_id)
    if not plan_orm:
        raise HTTPException(status_code=404, detail="Plan not found")

    plan = resolve_star_system(plan_orm, session)

    results = session.exec(
        select(ValidationResult)
        .where(ValidationResult.plan_id == plan_id)
        .order_by(ValidationResult.created_at.desc())
    ).all()

    program = session.exec(
        select(ObservingProgram).where(ObservingProgram.plan_id == plan_id)
    ).first()

    return templates.TemplateResponse(
        "plan_detail.html",
        {"request": request, "plan": plan, "results": results, "program": program, "user": user},
    )

# ============================================================
# Edit Science Plan (Astronomer only — DRAFT or INVALID plans)
# ============================================================

@app.get("/plans/{plan_id}/edit", response_class=HTMLResponse)
def edit_plan_form(
    plan_id: int,
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_role("Astronomer")),
):
    plan_orm = session.get(SciencePlan, plan_id)
    if not plan_orm:
        raise HTTPException(status_code=404, detail="Plan not found")

    if plan_orm.status not in ("DRAFT", "INVALID"):
        raise HTTPException(status_code=400, detail="Only DRAFT or INVALID plans can be edited")

    star = session.get(StarSystem, plan_orm.star_system_id)
    values = plan_orm.model_dump()
    values["star_system"] = star.name if star else ""
    values["schedule_start"] = plan_orm.schedule_start.strftime("%Y-%m-%dT%H:%M")
    values["schedule_end"] = plan_orm.schedule_end.strftime("%Y-%m-%dT%H:%M")

    return templates.TemplateResponse(
        "plan_edit.html",
        {
            "request": request,
            "plan_id": plan_id,
            "STAR_SYSTEMS": STAR_SYSTEMS,
            "TELESCOPE_LOCATIONS": TELESCOPE_LOCATIONS,
            "FILE_TYPES": FILE_TYPES,
            "FILE_QUALITIES": FILE_QUALITIES,
            "IMAGE_MODES": IMAGE_MODES,
            "errors": [],
            "values": values,
            "user": user,
        },
    )


@app.post("/plans/{plan_id}/edit")
def edit_plan(
    plan_id: int,
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_role("Astronomer")),
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
    plan_orm = session.get(SciencePlan, plan_id)
    if not plan_orm:
        raise HTTPException(status_code=404, detail="Plan not found")

    if plan_orm.status not in ("DRAFT", "INVALID"):
        raise HTTPException(status_code=400, detail="Only DRAFT or INVALID plans can be edited")

    errors = []

    star = session.exec(
        select(StarSystem).where(StarSystem.name == star_system)
    ).first()
    if not star:
        errors.append("Invalid star system selected.")

    def parse_dt(s: str) -> datetime:
        return datetime.fromisoformat(s)

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

    ok, field_errors = validate_science_plan_fields(data)
    if not ok:
        errors.extend(field_errors)

    if errors:
        data["star_system"] = star_system
        data["schedule_start"] = schedule_start
        data["schedule_end"] = schedule_end
        return templates.TemplateResponse(
            "plan_edit.html",
            {
                "request": request,
                "plan_id": plan_id,
                "STAR_SYSTEMS": STAR_SYSTEMS,
                "TELESCOPE_LOCATIONS": TELESCOPE_LOCATIONS,
                "FILE_TYPES": FILE_TYPES,
                "FILE_QUALITIES": FILE_QUALITIES,
                "IMAGE_MODES": IMAGE_MODES,
                "errors": errors,
                "values": data,
                "user": user,
            },
            status_code=400,
        )

    for field, value in data.items():
        setattr(plan_orm, field, value)
    plan_orm.status = "DRAFT"
    plan_orm.updated_at = datetime.utcnow()
    session.add(plan_orm)
    session.commit()

    return RedirectResponse(f"/plans/{plan_id}", status_code=303)


# ============================================================
# Delete Science Plan (Astronomer only — DRAFT or INVALID plans)
# ============================================================

@app.post("/plans/{plan_id}/delete")
def delete_plan(
    plan_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(require_role("Astronomer")),
):
    plan_orm = session.get(SciencePlan, plan_id)
    if not plan_orm:
        raise HTTPException(status_code=404, detail="Plan not found")

    if plan_orm.status not in ("DRAFT", "INVALID"):
        raise HTTPException(status_code=400, detail="Only DRAFT or INVALID plans can be deleted")

    # Cascade delete related records
    for result in session.exec(select(ValidationResult).where(ValidationResult.plan_id == plan_id)).all():
        session.delete(result)
    for program in session.exec(select(ObservingProgram).where(ObservingProgram.plan_id == plan_id)).all():
        session.delete(program)
    session.delete(plan_orm)
    session.commit()

    return RedirectResponse("/", status_code=303)


# ============================================================
# UC-02: Virtual Telescope Simulation (Astronomer only)
# ============================================================

@app.post("/plans/{plan_id}/simulate")
def simulate_plan(
    plan_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(require_role("Astronomer")),
):
    plan_orm = session.get(SciencePlan, plan_id)
    if not plan_orm:
        raise HTTPException(status_code=404, detail="Plan not found")

    _ok, messages = run_virtual_telescope_test(plan_orm)
    for msg in messages:
        session.add(ValidationResult(plan_id=plan_id, message=msg))
    session.commit()

    return RedirectResponse(f"/plans/{plan_id}", status_code=303)

# ============================================================
# UC-02: Official Validation (Science Observer only)
# ============================================================

@app.post("/plans/{plan_id}/validate")
def validate_plan(
    plan_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(require_role("ScienceObserver")),
):
    plan_orm = session.get(SciencePlan, plan_id)
    if not plan_orm:
        raise HTTPException(status_code=404, detail="Plan not found")

    approved, messages = run_official_validation(plan_orm)
    plan_orm.status = "VALID" if approved else "INVALID"
    plan_orm.updated_at = datetime.utcnow()

    for msg in messages:
        session.add(ValidationResult(plan_id=plan_id, message=f"[Official] {msg}"))
    session.add(plan_orm)
    session.commit()

    return RedirectResponse(f"/plans/{plan_id}", status_code=303)

# ============================================================
# UC-03: Submit Observing Program (Astronomer only)
# ============================================================

@app.get("/plans/{plan_id}/submit", response_class=HTMLResponse)
def submit_program_form(
    plan_id: int,
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_role("Astronomer")),
):
    plan_orm = session.get(SciencePlan, plan_id)
    if not plan_orm:
        raise HTTPException(status_code=404, detail="Plan not found")

    if plan_orm.status != "VALID":
        return templates.TemplateResponse(
            "submit_blocked.html",
            {"request": request, "plan": plan_orm, "user": user},
        )

    return templates.TemplateResponse(
        "submit_form.html",
        {
            "request": request,
            "plan": plan_orm,
            "CALIBRATION_UNITS": CALIBRATION_UNITS,
            "LIGHT_TYPES": LIGHT_TYPES,
            "FOLD_MIRROR_TYPES": FOLD_MIRROR_TYPES,
            "DIRECTIONS": DIRECTIONS,
            "errors": [],
            "values": {},
            "user": user,
        },
    )

@app.post("/plans/{plan_id}/submit")
def submit_program(
    plan_id: int,
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_role("Astronomer")),
    calibration_unit: str = Form(...),
    light_type: str = Form(...),
    fold_mirror_type: str = Form(...),
    teleposition_degree: float = Form(...),
    teleposition_direction: str = Form(...),
):
    plan_orm = session.get(SciencePlan, plan_id)
    if not plan_orm:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan_orm.status != "VALID":
        raise HTTPException(status_code=400, detail="Plan must be VALID to submit a program")

    data = dict(
        calibration_unit=calibration_unit,
        light_type=light_type,
        fold_mirror_type=fold_mirror_type,
        teleposition_degree=teleposition_degree,
        teleposition_direction=teleposition_direction,
    )

    ok, errors = validate_observing_program_fields(data)
    if not ok:
        return templates.TemplateResponse(
            "submit_form.html",
            {
                "request": request,
                "plan": plan_orm,
                "CALIBRATION_UNITS": CALIBRATION_UNITS,
                "LIGHT_TYPES": LIGHT_TYPES,
                "FOLD_MIRROR_TYPES": FOLD_MIRROR_TYPES,
                "DIRECTIONS": DIRECTIONS,
                "errors": errors,
                "values": data,
                "user": user,
            },
            status_code=400,
        )

    session.add(ObservingProgram(plan_id=plan_id, **data))
    plan_orm.status = "SUBMITTED"
    plan_orm.updated_at = datetime.utcnow()
    session.add(plan_orm)
    session.commit()

    return RedirectResponse(f"/plans/{plan_id}", status_code=303)

# ============================================================
# UC-04: Execute Observing Program (Telescope Operator only)
# ============================================================

@app.get("/programs", response_class=HTMLResponse)
def list_programs(
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_role("TelescopeOperator")),
):
    programs = session.exec(
        select(ObservingProgram).order_by(ObservingProgram.submitted_at.desc())
    ).all()

    return templates.TemplateResponse(
        "programs.html",
        {"request": request, "programs": programs, "user": user},
    )

@app.post("/programs/{program_id}/execute")
def execute_program(
    program_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(require_role("TelescopeOperator")),
):
    program = session.get(ObservingProgram, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    program.status = "Completed"
    session.add(program)
    session.commit()

    return RedirectResponse("/programs", status_code=303)

# ============================================================
# UC-05: Monitor Observation Progress (Science Observer only)
# ============================================================

@app.get("/monitoring", response_class=HTMLResponse)
def monitoring(
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_role("ScienceObserver")),
):
    programs = session.exec(
        select(ObservingProgram).order_by(ObservingProgram.submitted_at.desc())
    ).all()

    return templates.TemplateResponse(
        "monitoring.html",
        {"request": request, "programs": programs, "user": user},
    )