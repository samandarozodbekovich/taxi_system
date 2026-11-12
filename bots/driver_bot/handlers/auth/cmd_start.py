from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

from states.auth import AuthStates, RegisterStates


router = Router()

BTN_LOGIN = "🔐 Log in"
BTN_REGISTER = "📝 Register"

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    await state.update_data(telegram_id=message.from_user.id)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_LOGIN)],
            [KeyboardButton(text=BTN_REGISTER)]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "🚗 <b>Taxi Driver Panel</b>\n\n"
        "What would you like to do?",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    
@router.message(lambda m: m.text == BTN_REGISTER)
async def start_register(message: Message, state: FSMContext):
    await message.answer("👤 Enter your full name:")
    await state.set_state(RegisterStates.waiting_full_name)


@router.message(lambda m: m.text == BTN_LOGIN)
async def start_login(message: Message, state: FSMContext):
    await message.answer("🔑 Enter your driver code")
    await state.set_state(AuthStates.waiting_login)