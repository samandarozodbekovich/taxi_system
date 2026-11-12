from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from states.auth import RegisterStates
from functions import format_register_error
from services.api import driver_register

router = Router()

@router.message(RegisterStates.waiting_full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await message.answer("📱 Enter your phone number (+998901234567):")
    await state.set_state(RegisterStates.waiting_phone)


@router.message(RegisterStates.waiting_phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text.strip())
    await message.answer("🚗 Enter your car model (e.g. Cobalt):")
    await state.set_state(RegisterStates.waiting_car_model)


@router.message(RegisterStates.waiting_car_model)
async def get_car_model(message: Message, state: FSMContext):
    await state.update_data(car_model=message.text.strip())
    await message.answer("🎨 Enter your car color (e.g. White):")
    await state.set_state(RegisterStates.waiting_car_color)


@router.message(RegisterStates.waiting_car_color)
async def get_car_color(message: Message, state: FSMContext):
    await state.update_data(car_color=message.text.strip())
    await message.answer("🔢 Enter your car number (e.g. 01A123BC):")
    await state.set_state(RegisterStates.waiting_car_number)


@router.message(RegisterStates.waiting_car_number)
async def get_car_number(message: Message, state: FSMContext):
    await state.update_data(car_number=message.text.strip())
    await message.answer("🔒 Set a password (at least 6 characters):")
    await state.set_state(RegisterStates.waiting_password)


@router.message(RegisterStates.waiting_password)
async def get_password(message: Message, state: FSMContext):
    password = message.text.strip()
    await message.delete()   # hide the password

    if len(password) < 6:
        await message.answer("❌ The password must be at least 6 characters long. Please try again:")
        return

    data = await state.get_data()

    # Send to Django - including telegram_id
    result = await driver_register(
        full_name=data["full_name"],
        phone_number=data["phone_number"],
        car_model=data["car_model"],
        car_color=data["car_color"],
        car_number=data["car_number"],
        password=password,
        telegram_id=data["telegram_id"]   # ← /start da olgan ID
    )

    if result["success"]:
        # No token is issued: after admin approval the driver logs in via /start
        await state.clear()
        await message.answer(
            f"✅ <b>Registration successful!</b>\n\n"
            f"🔑 Your driver code: <code>{result['driver_code']}</code>\n"
            f"📌 Remember it — you will need it to log in!\n\n"
            f"⏳ An admin is reviewing your details. "
            f"Once approved, log in via /start.",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        # Show the Django error in a friendly form
        error_message = format_register_error(result["message"])

        await message.answer(
            error_message,
            parse_mode="HTML"
        )
        await state.clear()
