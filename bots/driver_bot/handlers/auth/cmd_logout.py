from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from services.api import driver_logout

router = Router()


@router.message(Command("logout"))
async def cmd_logout(message: Message, state: FSMContext):
    token = (await state.get_data()).get("token")
    if token and not await driver_logout(token):
        await message.answer("❌ Cannot reach the server. Please try again.")
        return

    # The token is revoked on the server - forget it here too
    await state.clear()
    await message.answer(
        "👋 You are logged out of the bot and the panel.\nPress /start to log in again.",
        reply_markup=ReplyKeyboardRemove()
    )
