import aiohttp
import logging
from config import API_BASE_URL

logger = logging.getLogger(__name__)

async def update_driver_telegram_id(driver_id: int, telegram_id: int) -> dict:
    url = f"{API_BASE_URL}/api/drivers/{driver_id}/telegram/"
    payload = {"telegram_id": telegram_id}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return {"success": True}
                return {"success": False}
    except Exception as e:
        logger.error(f"Telegram ID update xato: {e}")
        return {"success": False}