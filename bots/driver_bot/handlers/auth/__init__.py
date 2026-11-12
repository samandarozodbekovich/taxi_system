from .cmd_start import cmd_start
from .process_login import process_login
from .process_password import process_password
from .register import get_car_color, get_car_model, get_car_number, get_full_name, get_password, get_phone

from aiogram import Router

from .cmd_start import router as start_router
from .process_login import router as login_router
from .process_password import router as password_router
from .register import router as register_router 

# Combine all routers into one
router = Router()
router.include_router(start_router)
router.include_router(login_router)
router.include_router(register_router)
router.include_router(password_router)