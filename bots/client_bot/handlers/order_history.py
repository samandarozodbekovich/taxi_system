import html

from aiogram import F, Router, types

from keyboards import BTN_ORDER_HISTORY
from services.api import get_order_history

router = Router()

STATUS_LABELS = {
    "SEARCHING": "🔍 Searching", "ACCEPTED": "🚗 Accepted", "WAITING": "⏳ Driver waiting",
    "IN_PROGRESS": "🏁 In progress", "COMPLETED": "✅ Completed", "CANCELED": "❌ Canceled",
    "NO_DRIVER": "😔 No driver found",
}


@router.message(F.text == BTN_ORDER_HISTORY)
async def order_history(message: types.Message):
    orders = await get_order_history(message.from_user.id)
    if orders is None:
        await message.answer("Could not load your orders. Please try /start.")
        return
    if not orders:
        await message.answer("You have no orders yet.")
        return

    lines = ["📋 <b>Your latest orders:</b>"]
    for order in orders:
        lines.append(
            f"\n<b>{order['order_number']}</b> · {order['created_at'][:10]} · {STATUS_LABELS.get(order['status'], order['status'])}\n"
            f"📍 {html.escape(order['pickup_address'] or '')}\n"
            f"🏁 {html.escape(order['destination_address'] or '—')}\n"
            f"💵 {float(order['total_price']):,.0f} UZS"
        )
    await message.answer("\n".join(lines), parse_mode="HTML")
