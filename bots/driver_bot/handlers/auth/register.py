from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.auth import RegisterStates
from services.api import driver_register
from keyboards.main_menu import get_main_menu

router = Router()

@router.message(RegisterStates.waiting_full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await message.answer("📱 Telefon raqamingizni kiriting (+998901234567):")
    await state.set_state(RegisterStates.waiting_phone)


@router.message(RegisterStates.waiting_phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text.strip())
    await message.answer("🚗 Mashina modelini kiriting (masalan: Cobalt):")
    await state.set_state(RegisterStates.waiting_car_model)


@router.message(RegisterStates.waiting_car_model)
async def get_car_model(message: Message, state: FSMContext):
    await state.update_data(car_model=message.text.strip())
    await message.answer("🎨 Mashina rangini kiriting (masalan: Oq):")
    await state.set_state(RegisterStates.waiting_car_color)


@router.message(RegisterStates.waiting_car_color)
async def get_car_color(message: Message, state: FSMContext):
    await state.update_data(car_color=message.text.strip())
    await message.answer("🔢 Mashina raqamini kiriting (masalan: 01A123BC):")
    await state.set_state(RegisterStates.waiting_car_number)


@router.message(RegisterStates.waiting_car_number)
async def get_car_number(message: Message, state: FSMContext):
    await state.update_data(car_number=message.text.strip())
    await message.answer("🔒 Parol o'rnating (kamida 6 ta belgi):")
    await state.set_state(RegisterStates.waiting_password)


@router.message(RegisterStates.waiting_password)
async def get_password(message: Message, state: FSMContext):
    password = message.text.strip()
    await message.delete()   # parol ko'rinmasin

    if len(password) < 6:
        await message.answer("❌ Parol kamida 6 ta belgi bo'lishi kerak. Qayta kiriting:")
        return

    data = await state.get_data()

    # Django ga yuboramiz — telegram_id ham birga
    result = await driver_register(
        full_name=data["full_name"],
        phone_number=data["phone_number"],
        car_model=data["car_model"],
        car_color=data["car_color"],
        car_number=data["car_number"],
        password=password,
        telegram_id=data["telegram_id"]   # ← /start da olgan ID
    )

    if result["success"]:
        await state.set_state(None)
        await state.update_data(
            driver_id=result["driver_id"],
            is_online=False
        )
        await message.answer(
            f"✅ <b>Ro'yxatdan muvaffaqiyatli o'tdingiz!</b>\n\n"
            f"🔑 Driver kodingiz: <code>{result['driver_code']}</code>\n"
            f"📌 Uni eslab qoling — kirish uchun kerak bo'ladi!",
            parse_mode="HTML",
            reply_markup=get_main_menu(is_online=False)
        )
    else:
        # Django dan kelgan xatoni chiroyli ko'rsatamiz
        error_message = format_register_error(result["message"])

        await message.answer(
            error_message,
            parse_mode="HTML"
        )
        await state.clear()
        
        
def format_register_error(raw_message: str) -> str:
    """
    Django xato xabarlarini foydalanuvchiga qulay ko'rinishga o'tkazadi.
    """
    # Allaqachon ro'yxatdan o'tgan
    if "telegram_id" in raw_message and "already exists" in raw_message:
        return (
            "⚠️ <b>Siz allaqachon ro'yxatdan o'tgansiz!</b>\n\n"
            "Tizimga kirish uchun driver kodingizni ishlating.\n\n"
            "👇 Kirish uchun /start bosing"
        )

    if "phone_number" in raw_message and "already exists" in raw_message:
        return (
            "⚠️ <b>Bu telefon raqam allaqachon ro'yxatdan o'tgan!</b>\n\n"
            "Boshqa raqam kiriting yoki /start orqali tizimga kiring."
        )

    if "car_number" in raw_message and "already exists" in raw_message:
        return (
            "⚠️ <b>Bu mashina raqami allaqachon ro'yxatdan o'tgan!</b>\n\n"
            "Boshqa mashina raqami kiriting yoki /start orqali murojaat qiling."
        )

    # Umumiy xato
    return (
        "❌ <b>Ro'yxatdan o'tishda xatolik yuz berdi.</b>\n\n"
        "Qayta urinib ko'ring yoki /start bosing."
    )