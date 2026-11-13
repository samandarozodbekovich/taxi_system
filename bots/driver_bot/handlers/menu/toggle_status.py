from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from services.api import get_driver_profile, set_driver_status
from keyboards.main_menu import BTN_GO_OFFLINE, BTN_GO_ONLINE, get_main_menu

router = Router()

@router.message(F.text.in_([BTN_GO_OFFLINE, BTN_GO_ONLINE]))
async def toggle_status(message: Message, state: FSMContext):
    data = await state.get_data()
    driver_id = data.get("driver_id")
    token = data.get("token")
    if not driver_id or not token:
        await message.answer("❌ Error: driver data not found. Please log in again via /start.")
        return

    # The status may have been changed in the panel - read it from the server, not from the bot's copy
    profile = await get_driver_profile(token)
    if not profile["success"]:
        if profile.get("auth_failed"):
            await state.clear()
        await message.answer(f"Error: {profile['message']}")
        return

    driver = profile["driver"]
    if driver["status"] == "BUSY":
        await message.answer("🚗 You are on a trip. Finish it first.", reply_markup=get_main_menu(True))
        return
    new_status = not driver["is_online"]

    result = await set_driver_status(driver_id, new_status, token)

    if result.get("auth_failed"):
        await state.clear()

    if result["success"]:
        await state.update_data(is_online=new_status)
        status_text = "🟢 Online" if new_status else "🔴 Offline"
        await message.answer(
            f"✅ Status changed: {status_text}",
            parse_mode="HTML",
            reply_markup=get_main_menu(new_status)
            )
    else:
        await message.answer(f"Error: {result['message']}")
