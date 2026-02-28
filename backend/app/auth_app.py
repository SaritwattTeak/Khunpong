from typing import Optional
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
from passlib.context import CryptContext

# =========================
# App Setup
# =========================

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

templates = Jinja2Templates(directory="templates")

# =========================
# Database Setup
# =========================

DB_URL = "sqlite:///./gemini.db"
engine = create_engine(DB_URL, echo=False)

# =========================
# Password Hashing
# =========================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# =========================
# User Model
# =========================

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: str

# =========================
# DB Utilities
# =========================

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def get_current_user(request: Request):
    return request.session.get("user")

# =========================
# Startup
# =========================

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# =========================
# Login Page
# =========================

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# =========================
# Login Logic
# =========================

@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password"}
        )

    request.session["user"] = {
        "id": user.id,
        "username": user.username,
        "role": user.role
    }

    return RedirectResponse(url="/dashboard", status_code=303)

# =========================
# Dashboard (Protected)
# =========================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = get_current_user(request)

    if not user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user}
    )

# =========================
# Logout
# =========================

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


# =========================
# Create First User (Optional Helper)
# =========================

@app.get("/create-admin")
def create_admin():
    with Session(engine) as session:
        existing = session.exec(
            select(User).where(User.username == "admin")
        ).first()

        if existing:
            return {"message": "Admin already exists"}

        user = User(
            username="admin",
            password_hash=hash_password("1234"),
            role="admin"
        )
        session.add(user)
        session.commit()

        return {"message": "Admin created (username=admin, password=1234)"}