from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import WebAppInfo
from config import WEBAPP_URL

# Button labels are shared with the handlers that match on them (F.text == ...)
BTN_GO_ONLINE = "🟢 Go online"
BTN_GO_OFFLINE = "🔴 Go offline"
BTN_OPEN_PANEL = "🚗 Open panel"
BTN_BALANCE = "💰 Balance"


def get_main_menu(is_online: bool) -> ReplyKeyboardMarkup:

    status_btn = KeyboardButton(
        text=BTN_GO_OFFLINE if is_online else BTN_GO_ONLINE
    )
    webapp_btn = KeyboardButton(
        text=BTN_OPEN_PANEL,
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    wallet_btn = KeyboardButton(text=BTN_BALANCE)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [status_btn],
            [webapp_btn],
            [wallet_btn]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard
