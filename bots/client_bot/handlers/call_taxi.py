from aiogram import F, Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from keyboards import BTN_CALL_TAXI
from loader import WEBAPP_URL

router = Router()


@router.message(F.text == BTN_CALL_TAXI)
async def call_taxi(message: types.Message):
    # Orders are placed in the Mini App (pickup and destination on the map). An inline button
    # is used because it passes signed initData, which the backend verifies.
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🗺 Open the taxi app", web_app=WebAppInfo(url=WEBAPP_URL))
    ]])
    await message.answer("Choose the pickup point and destination on the map:", reply_markup=keyboard)


@router.message(F.location)
async def location_sent(message: types.Message):
    await message.answer(f"To order a taxi, press \"{BTN_CALL_TAXI}\" and choose the points on the map.")
