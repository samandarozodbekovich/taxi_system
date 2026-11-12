import aiohttp
import logging
from config import API_BASE_URL

logger = logging.getLogger(__name__)


async def driver_register(full_name, phone_number, car_model,
                           car_color, car_number, password, telegram_id) -> dict:
    url = f"{API_BASE_URL}/api/drivers/register/"
    payload = {
        "full_name": full_name,
        "phone_number": phone_number,
        "car_model": car_model,
        "car_color": car_color,
        "car_number": car_number,
        "password": password,
        "telegram_id": telegram_id   # passed in here
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                data = await response.json()
                if response.status == 201:
                    return {
                        "success": True,
                        "driver_code": data.get("driver_code"),  # .get() is safe
                        "driver_id": data.get("id"),             # .get() is safe
                    }
                return {"success": False, "message": str(data)}
    except Exception as e:
        logger.error(f"Register API error: {e}")
        return {"success": False, "message": "Cannot reach the server"}