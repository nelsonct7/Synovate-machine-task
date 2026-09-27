"""Collects every route module into a single router."""

from fastapi import APIRouter

from app.api.routes import assistant, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(assistant.router)
