from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS
from .database import Base, engine
from .routers import adventures, students, submissions

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Next Universe — AI Learning Game Platform",
    description=(
        "POC backend: transforms a baseline curriculum into personalized, "
        "story-driven coding missions rendered by a deterministic game engine."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router, prefix="/api")
app.include_router(adventures.router, prefix="/api")
app.include_router(submissions.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
