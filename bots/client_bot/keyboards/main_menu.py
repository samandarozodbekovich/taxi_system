from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Button labels are shared with the handlers that match on them (F.text == ...)
BTN_CALL_TAXI = "🚖 Call a taxi"
BTN_MY_BONUSES = "💰 My bonuses"
BTN_ORDER_HISTORY = "📋 Order history"

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_CALL_TAXI)],
        [KeyboardButton(text=BTN_MY_BONUSES), KeyboardButton(text=BTN_ORDER_HISTORY)],
    ],
    resize_keyboard=True
)
