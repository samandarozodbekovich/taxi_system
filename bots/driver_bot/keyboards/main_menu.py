from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import WebAppInfo
from config import WEBAPP_URL


def get_main_menu(is_online: bool) -> ReplyKeyboardMarkup:
    
    status_btn = KeyboardButton(
        text="🔴 Offline bo'lish" if is_online else "🟢 Online bo'lish"
    )
    webapp_btn = KeyboardButton(
        text="🚗 Panelni ochish",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    wallet_btn = KeyboardButton(text="💰 Balans")
    
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
