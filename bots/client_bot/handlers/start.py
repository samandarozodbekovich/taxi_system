from aiogram import F, Router, types
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from keyboards import main_menu
from services.api import get_client_by_tg_id, register_client

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject, state: FSMContext):
    client = await get_client_by_tg_id(message.from_user.id)
    if client:
        await message.answer(f"Welcome, {client.get('full_name', 'there')}!", reply_markup=main_menu)
        return

    # A referral link t.me/<bot>?start=<code> passes the inviter's code - keep it until registration
    await state.update_data(invited_by_code=command.args or "")
    await message.answer(
        "Please register to use the service. Share your contact:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📲 Share contact", request_contact=True)]],
            resize_keyboard=True
        )
    )


@router.message(F.contact)
async def handle_contact(message: types.Message, state: FSMContext):
    # Only the user's own contact may be used for registration
    if message.contact.user_id != message.from_user.id:
        await message.answer("Please share your own contact.")
        return

    data = await state.get_data()
    success = await register_client({
        "telegram_id": message.from_user.id,
        "full_name": message.from_user.full_name,
        "username": message.from_user.username,
        "phone_number": message.contact.phone_number,
        "language_code": message.from_user.language_code or 'uz',
        "invited_by_code": data.get("invited_by_code", ""),
    })

    if success:
        await state.clear()
        await message.answer("You are registered!", reply_markup=main_menu)
    else:
        await message.answer("Something went wrong. Please try again.")
