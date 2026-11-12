from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.auth import AuthStates
from services.api import driver_login
from keyboards.main_menu import get_main_menu

router = Router()

@router.message(AuthStates.waiting_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    login = data.get("login")

    await message.delete()

    result = await driver_login(login, password)

    if result["success"]:
        driver = result["driver"]
        is_online = driver.get("is_online", False)

        # Clear the state but keep the data
        await state.set_state(None)
        await state.update_data(
            driver_id=driver["id"],
            token=driver.get("token"),   # for backend requests
            driver_name=driver["full_name"],
            is_online=is_online
        )

        text = (
            f"✅ <b>Welcome, {driver['full_name']}!</b>\n\n"
            f"🚗 Car: {driver.get('car_model', '—')} | {driver.get('car_number', '—')}\n"
            f"Status: {'🟢 Online' if is_online else '🔴 Offline'}"
        )

        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_main_menu(is_online)
        )

    else:
        await message.answer(
            f"❌ {result['message']}\n\nPlease enter your driver code again:",
            parse_mode="HTML"
        )
        await state.set_state(AuthStates.waiting_login) 