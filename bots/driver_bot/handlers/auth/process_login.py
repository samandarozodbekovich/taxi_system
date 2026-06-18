from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from django.db import router

from states.auth import AuthStates

router = Router()

@router.message(AuthStates.waiting_login)
async def process_login(message: Message, state: FSMContext):
    login = message.text.strip()
    
    if len(login) < 3:
        await message.answer("Login kamida 3 ta belgidan iborat bo'lishi kerak. Iltimos, qayta urinib ko'ring.")
        return
    
    await state.update_data(login=login)
    await message.answer("🔑 Parolingizni kiriting:")
    await state.set_state(AuthStates.waiting_password)