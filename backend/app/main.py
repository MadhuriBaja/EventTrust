from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, investigations
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Evidence-based pre-registration investigation agent API",
)

# Enable CORS for local development
# Allow requests from the configured frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
app.include_router(investigations.router, prefix=settings.api_prefix, tags=["investigations"])


@app.get("/")
def read_root():
    return {"message": "EventTrust API is running"}


@app.get("/health")
def read_health():
    return {"status": "ok"}
