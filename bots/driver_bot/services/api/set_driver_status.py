import aiohttp
import logging
from config import API_BASE_URL

logger = logging.getLogger(__name__)

async def set_driver_status(driver_id: int, is_online: bool, token: str) -> dict:
    url = f"{API_BASE_URL}/api/drivers/{driver_id}/status/"
    payload = {"is_online": is_online}
    # The backend resolves the driver from this token (obtained on login/registration)
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"success": True, "status": data.get("status")}
                if response.status == 401:
                    return {"success": False, "auth_failed": True,
                            "message": "Session expired. Press /start to log in again."}
                return {"success": False, "message": "Could not change the status"}
    except Exception as e:
        logger.error(f"Status API error: {e}")
        return {"success": False, "message": "Cannot reach the server"}
