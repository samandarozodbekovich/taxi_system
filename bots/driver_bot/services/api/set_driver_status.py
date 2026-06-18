import aiohttp
import logging
from config import API_BASE_URL

logger = logging.getLogger(__name__)

async def set_driver_status(driver_id: int, is_online: bool) -> dict:
    url = f"{API_BASE_URL}/api/drivers/{driver_id}/status/"
    payload = {"is_online": is_online}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                data = await response.json()
                if response.status == 200:
                    return {"success": True, "status": data.get("status")}
                else:
                    return {"success": False, "message": "Status o'zgartirib bo'lmadi"}
    except Exception as e:
        logger.error(f"Status API xatolik: {e}")
        return {"success": False, "message": "Server bilan aloqa yo'q"}