from fastapi import FastAPI
from app.api.routes import health
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Evidence-based pre-registration investigation agent API",
)

app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])


@app.get("/")
def read_root():
    return {"message": "EventTrust API is running"}


@app.get("/health")
def read_health():
    return {"status": "ok"}
