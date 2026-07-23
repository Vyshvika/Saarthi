import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
import models  # noqa: F401 - ensures models are registered before create_all
from auth_router import router as auth_router
from chat_router import router as chat_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Saarthi API")

# Always allow local dev. Add your main deployed frontend URL via the
# FRONTEND_URL env var (comma-separated if you have more than one), e.g.
#   FRONTEND_URL=https://saarthi-ruby.vercel.app
allowed_origins = ["http://localhost:5173"]
frontend_url_env = os.getenv("FRONTEND_URL", "")
if frontend_url_env:
    allowed_origins += [u.strip() for u in frontend_url_env.split(",") if u.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # Also allow any Vercel preview URL for this project (e.g.
    # saarthi-hwa6n3bri-kotagirivyshvika-6989s-projects.vercel.app), so a new
    # preview deploy on every push doesn't need a manual CORS update each time.
    allow_origin_regex=r"https://saarthi.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {"status": "ok", "service": "saarthi"}