from .show_wallet import show_wallet, router
from .toggle_status import toggle_status, router

from aiogram import Router

from .my_trips import router as my_trips
from .show_wallet import router as show_wallet
from .toggle_status import router as toggle_status

# Combine all routers into one
router = Router()
router.include_router(show_wallet)
router.include_router(toggle_status)
router.include_router(my_trips)
