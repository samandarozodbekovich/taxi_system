from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from services.api import set_driver_status
from keyboards.main_menu import get_main_menu

router = Router()

@router.message(F.text.in_(["🔴 Offline bo'lish", "🟢 Online bo'lish"]))
async def toggle_status(message: Message, state: FSMContext):
    data = await state.get_data()
    driver_id = data.get("driver_id")
    if not driver_id:
        await message.answer("❌ Xatolik: Haydovchi ma'lumotlari topilmadi. Iltimos, qayta kiring.")
        return
    
    is_online = data.get("is_online", False)
    new_status = not is_online
    
    result = await set_driver_status(driver_id, new_status)
    
    if result["success"]:
        await state.update_data(is_online=new_status)
        status_text = "🟢 Online" if new_status else "🔴 Offline"
        await message.answer(
            f"✅ Holat muvaffaqiyatli o'zgartirildi: {status_text}",
            parse_mode="HTML",
            reply_markup=get_main_menu(new_status)
            )
    else:
        await message.answer(f"Xatolik: {result['message']}")
    