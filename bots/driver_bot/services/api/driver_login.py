import aiohttp
import logging
from config import API_BASE_URL

logger = logging.getLogger(__name__)

async def driver_login(login: str, password: str) -> dict:
    url = f"{API_BASE_URL}/api/drivers/login/"
    payload = {"driver_code": login, "password": password}  # ← driver_code !

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                data = await response.json()
                if response.status == 200:
                    return {"success": True, "driver": data}
                else:
                    # On 429 (IP throttle) DRF returns "detail"
                    error = data.get("non_field_errors", [data.get("detail", "Error")])[0]
                    return {"success": False, "message": error}
    except Exception as e:
        logger.error(f"Login API error: {e}")
        return {"success": False, "message": "Cannot reach the server"}
    