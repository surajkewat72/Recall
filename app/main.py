import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Update this in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    os.makedirs("app/static", exist_ok=True)
    app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

    @app.get("/health", tags=["system"])
    def health_check():
        """Health check endpoint."""
        return {
            "status": "ok",
            "project": settings.PROJECT_NAME
        }

    return app

app = create_app()
