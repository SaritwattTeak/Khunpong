from typing import Optional
from sqlmodel import SQLModel, Field, create_engine

# =========================
# Database Setup
# =========================

DB_URL = "sqlite:///./gemini.db"
engine = create_engine(DB_URL, echo=False)

# =========================
# User Model
# =========================

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: str

# =========================
# Create Tables
# =========================

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# =========================
# Run
# =========================

if __name__ == "__main__":
    create_db_and_tables()
    print("✅ User table created successfully.")