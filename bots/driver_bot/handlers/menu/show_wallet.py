from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from services.api import set_driver_status, get_driver_wallet
from keyboards.main_menu import BTN_BALANCE, get_main_menu

router = Router()



@router.message(F.text == BTN_BALANCE)
async def show_wallet(message: Message, state:FSMContext):
    data = await state.get_data()
    driver_id = data.get("driver_id")
    token = data.get("token")

    if not driver_id or not token:
        await message.answer("❌ Please log in: /start")
        return

    result = await get_driver_wallet(token)

    if result["success"]:
        balance = result["balance"]
        await message.answer(
            f"💰 <b>Your balance:</b> {balance:,.0f} UZS",
            parse_mode="HTML"
        )
    else:
        await message.answer(f"❌ {result['message']}")