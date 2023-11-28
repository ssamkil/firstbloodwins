from fastapi import APIRouter
from .route import user

router = APIRouter()

router.include_router(user)