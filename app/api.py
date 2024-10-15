from fastapi import APIRouter

from app.auth.views import auth_router
from app.referrals.views import router as referrals_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(referrals_router, prefix="/referrals", tags=["referrals"])