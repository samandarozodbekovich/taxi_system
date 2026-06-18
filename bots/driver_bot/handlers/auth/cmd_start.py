from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from django.db import router

from states.auth import AuthStates, RegisterStates


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    await state.update_data(telegram_id=message.from_user.id)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔐 Kirish")],
            [KeyboardButton(text="📝 Ro'yxatdan o'tish")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "🚗 <b>Taxi Driver Paneli</b>\n\n"
        "Nima qilmoqchisiz?",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    
@router.message(lambda m: m.text == "📝 Ro'yxatdan o'tish")
async def start_register(message: Message, state: FSMContext):
    await message.answer("👤 Ismingizni kiriting (To'liq ism):")
    await state.set_state(RegisterStates.waiting_full_name)


@router.message(lambda m: m.text == "🔐 Kirish")
async def start_login(message: Message, state: FSMContext):
    await message.answer("🔑 Driver kodingizni kiriting")
    await state.set_state(AuthStates.waiting_login)