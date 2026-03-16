from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import get_settings
from backend.db.database import init_db
from backend.api.routers import careers, predictions, comparisons, recommendations, chat

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered career prediction platform — predict how AI will impact your career",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(careers.router)
app.include_router(predictions.router)
app.include_router(comparisons.router)
app.include_router(recommendations.router)
app.include_router(chat.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "app": settings.app_name, "version": settings.app_version}
