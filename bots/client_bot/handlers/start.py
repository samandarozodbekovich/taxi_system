from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from services.api import create_taxi_order, get_client_by_tg_id, register_client

router = Router()

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚖 Call a taxi", request_location=True)],
        [KeyboardButton(text="💰 My bonuses"), KeyboardButton(text="📋 Order history")]
    ],
    resize_keyboard=True
)

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    client = await get_client_by_tg_id(user_id)
    
    if client:
        await message.answer(
            f"Welcome, {client.get('full_name', 'there')}!", 
            reply_markup=main_menu
        )
    else:
        # The client is not in the database - ask them to register
        await message.answer(
            "Please register to use the service. Share your contact:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="📲 Share contact", request_contact=True)]],
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
        await message.answer("You are registered!", reply_markup=main_menu)
    else:
        await message.answer("Something went wrong. Please try again.")
        
        
@router.message(F.location)
async def handle_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude
    
    await message.answer(f"Your location: latitude {lat}, longitude {lon}. Calling a taxi from the bot is still in development.")
    
    order_data = {
        "client_telegram_id": message.from_user.id,
        "pickup_latitude": lat,
        "pickup_longitude": lon,
        "pickup_address": "Telegram location",
        "destination_latitude": 0,
        "destination_longitude": 0,
        "destination_address": "Not specified" 
    }
    
    result, status_code = await create_taxi_order(order_data)
    
    if status_code == 201:
        await message.answer("Order received! We will find a driver shortly.")
    else:
        error_msg = result.get("error", "Something went wrong")
        await message.answer(f"Something went wrong: {error_msg}")
    