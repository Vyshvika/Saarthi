# Saarthi backend

1. `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in `AI_API_KEY` and `JWT_SECRET`
4. `uvicorn main:app --reload --port 8000`

The SQLite database file (`saarthi.db`) is created automatically on first run.
