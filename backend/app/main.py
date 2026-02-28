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
)
from .services import (
    validate_science_plan_fields,
)

# ============================================================
# App Setup
# ============================================================

app = FastAPI(title="Gemini Project Prototype (Simulation Version)")

templates = Jinja2Templates(directory="app/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        if not session.exec(select(User)).first():

            session.add(User(
                username="astro",
                password_hash=hash_password("astro123"),
                role="Astronomer"
            ))

            session.add(User(
                username="observer",
                password_hash=hash_password("observer123"),
                role="ScienceObserver"
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
    plans = session.exec(
        select(SciencePlan).order_by(SciencePlan.created_at.desc())
    ).all()

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