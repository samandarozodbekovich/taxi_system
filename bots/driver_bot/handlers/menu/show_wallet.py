from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from services.api import set_driver_status, get_driver_wallet
from keyboards.main_menu import get_main_menu

router = Router()



@router.message(F.text == "💰 Balans")
async def show_wallet(message: Message, state:FSMContext):
    data = await state.get_data()
    driver_id = data.get("driver_id")

    if not driver_id:
        await message.answer("❌ Tizimga kiring. /start")
        return

    result = await get_driver_wallet(driver_id)
    
    if result["success"]:
        balance = result["balance"]
        await message.answer(
            f"💰 <b>Balansingiz:</b> {balance:,} so'm",
            parse_mode="HTML"
        )
    else:
        await message.answer(f"❌ {result['message']}")