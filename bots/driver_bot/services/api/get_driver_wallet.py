import aiohttp
import logging
from config import API_BASE_URL

logger = logging.getLogger(__name__)


async def get_driver_wallet(driver_id: int) -> dict:
    url = f"{API_BASE_URL}/api/wallet/{driver_id}/"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if response.status == 200:
                    return {"success": True, "balance": data.get("balance", 0)}
                else:
                    return {"success": False, "message": "Balans topilmadi"}
    except Exception as e:
        logger.error(f"Wallet API xatolik: {e}")
        return {"success": False, "message": "Server bilan aloqa yo'q"}