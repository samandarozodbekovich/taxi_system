from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.api_service import create_taxi_order, get_client_by_tg_id, register_client

router = Router()

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚖 Taxi chaqirish", request_location=True)],
        [KeyboardButton(text="💰 Bonuslarim"), KeyboardButton(text="📋 Buyurtmalar tarixim")]
    ],
    resize_keyboard=True
)

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    client = await get_client_by_tg_id(user_id)
    
    if client:
        await message.answer(
            f"Xush kelibsiz, {client.get('full_name', 'Mijoz')}!", 
            reply_markup=main_menu
        )
    else:
        # Agar mijoz bazada bo'lmasa, uni ro'yxatdan o'tishga yo'naltirish kerak
        await message.answer(
            "Tizimdan foydalanish uchun ro'yxatdan o'ting. Iltimos, kontaktingizni yuboring:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="📲 Kontaktni yuborish", request_contact=True)]],
                resize_keyboard=True
            )
        )
        
        
@router.message(F.contact)
async def handle_contact(message: types.Message):
    data = {
        "telegram_id": message.from_user.id,
        "full_name": message.from_user.full_name,
        "username": message.from_user.username,
        "phone_number": message.contact.phone_number,
        "language_code": message.from_user.language_code or 'uz'
    }
    
    success = await register_client(data)
    
    if success:
        await message.answer("Siz muvaffaqiyatli ro'yxatdan o'tdingiz!", reply_markup=main_menu)
    else:
        await message.answer("Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")
        
        
@router.message(F.location)
async def handle_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude
    
    await message.answer(f"Sizning joylashuvingiz: Latitude {lat}, Longitude {lon}. Taxi chaqirish funksiyasi hozircha ishlab chiqilmoqda.")
    
    order_data = {
        "client_telegram_id": message.from_user.id,
        "pickup_latitude": lat,
        "pickup_longitude": lon,
        "pickup_address": "Telegram location",
        "destination_latitude": 0,
        "destination_longitude": 0,
        "destination_address": "Aniqlanmagan" 
    }
    
    result, status_code = await create_taxi_order(order_data)
    
    if status_code == 201:
        await message.answer("Buyurtma qabul qilindi! Haydovchi tez orada topiladi")
    else:
        error_msg = result.get("error", "Xatolik yuz berdi")
        await message.answer(f"Xatolik yuz berdi: {error_msg}")
    