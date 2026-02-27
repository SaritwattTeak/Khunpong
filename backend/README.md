# Gemini Prototype Web App (UC-01..UC-03)

Implements:
- UC-01 Create Science Plan
- UC-02 Validate Science Plan (virtual telescope simulation)
- UC-03 Submit Observing Program (requires VALID plan)

## Run (backend)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Open: http://127.0.0.1:8000
