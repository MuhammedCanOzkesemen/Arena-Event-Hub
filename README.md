# arena-event-hub

A clean, interview-friendly backend project for a sports event calendar.

## Stack
- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- SQLite
- Pydantic
- Jinja2 + Bootstrap 5
- pytest
- uvicorn

## Run locally (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:
- API docs: <http://127.0.0.1:8000/docs>
- HTML pages: <http://127.0.0.1:8000/events>

## Test
```powershell
pytest
```
