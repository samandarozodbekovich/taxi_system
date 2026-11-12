from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states.auth import AuthStates

router = Router()

@router.message(AuthStates.waiting_login)
async def process_login(message: Message, state: FSMContext):
    login = message.text.strip()
    
    if len(login) < 3:
        await message.answer("The login must be at least 3 characters long. Please try again.")
        return
    
    await state.update_data(login=login)
    await message.answer("🔑 Enter your password:")
    await state.set_state(AuthStates.waiting_password)