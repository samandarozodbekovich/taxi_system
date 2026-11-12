import html

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.main_menu import BTN_MY_TRIPS
from services.api import get_driver_trips

router = Router()

STATUS_LABELS = {
    "ACCEPTED": "🚗 Accepted", "WAITING": "⏳ Waiting", "IN_PROGRESS": "🏁 In progress",
    "COMPLETED": "✅ Completed", "CANCELED": "❌ Canceled",
}


@router.message(F.text == BTN_MY_TRIPS)
async def my_trips(message: Message, state: FSMContext):
    token = (await state.get_data()).get("token")
    if not token:
        await message.answer("❌ Please log in: /start")
        return

    result = await get_driver_trips(token)
    if not result["success"]:
        await message.answer(f"❌ {result['message']}")
        return
    if not result["trips"]:
        await message.answer("You have no trips yet.")
        return

    lines = ["📋 <b>Your latest trips:</b>"]
    for trip in result["trips"]:
        lines.append(
            f"\n<b>{trip['order_number']}</b> · {trip['created_at'][:10]} · {STATUS_LABELS.get(trip['status'], trip['status'])}\n"
            f"📍 {html.escape(trip['pickup_address'] or '')}\n"
            f"🏁 {html.escape(trip['destination_address'] or '—')}\n"
            f"💵 {float(trip['total_price']):,.0f} UZS"
        )
    await message.answer("\n".join(lines), parse_mode="HTML")
