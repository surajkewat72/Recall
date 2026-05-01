from fastapi import APIRouter

api_router = APIRouter()

# Example router placeholder
# from app.api.routers import search
# api_router.include_router(search.router, prefix="/search", tags=["search"])

@api_router.get("/status")
def api_status():
    """Simple API status check."""
    return {"status": "operational"}
