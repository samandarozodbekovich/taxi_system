import aiohttp
import logging
from config import API_BASE_URL

logger = logging.getLogger(__name__)


async def get_driver_profile(token: str) -> dict:
    # Backend endpoint: GET /api/drivers/me/ - the current status, also when changed in the panel
    url = f"{API_BASE_URL}/api/drivers/me/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return {"success": True, "driver": await response.json()}
                if response.status == 401:
                    return {"success": False, "auth_failed": True,
                            "message": "Session expired. Press /start to log in again."}
                return {"success": False, "message": "Could not load your profile"}
    except Exception as e:
        logger.error(f"Profile API error: {e}")
        return {"success": False, "message": "Cannot reach the server"}
