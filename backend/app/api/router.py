from fastapi import APIRouter

from app.api.endpoints import evaluate, projects

api_router = APIRouter()
api_router.include_router(evaluate.router, tags=["evaluate"])
api_router.include_router(projects.router, tags=["projects"])
