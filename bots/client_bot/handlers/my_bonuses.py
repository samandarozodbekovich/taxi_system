from aiogram import F, Router, types

from keyboards import BTN_MY_BONUSES
from services.api import get_client_bonus

router = Router()


@router.message(F.text == BTN_MY_BONUSES)
async def my_bonuses(message: types.Message):
    bonus = await get_client_bonus(message.from_user.id)
    if bonus is None:
        await message.answer("Could not load your bonuses. Please try /start.")
        return

    bot_username = (await message.bot.get_me()).username
    await message.answer(
        f"💰 <b>Bonus balance:</b> {float(bonus['bonus_balance']):,.0f} UZS\n"
        f"👥 <b>Friends invited:</b> {bonus['invited_count']}\n\n"
        f"Invite friends with your link - you get a bonus after their first trip:\n"
        f"https://t.me/{bot_username}?start={bonus['referral_code']}",
        parse_mode="HTML",
    )
