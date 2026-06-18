from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Qabul qilish",
                    callback_data=f"accept_order:{order_id}"
                    ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"reject_order:{order_id}"
                )
            ]
        ]
    )
    return keyboard
