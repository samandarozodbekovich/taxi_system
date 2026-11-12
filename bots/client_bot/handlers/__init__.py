from aiogram import Router

from .call_taxi import router as call_taxi_router
from .my_bonuses import router as my_bonuses_router
from .order_history import router as order_history_router
from .start import router as start_router

# Combine all routers into one
router = Router()
router.include_router(start_router)
router.include_router(call_taxi_router)
router.include_router(my_bonuses_router)
router.include_router(order_history_router)
