import aiohttp
import logging
from config import API_BASE_URL

logger = logging.getLogger(__name__)


async def driver_logout(token: str) -> bool:
    # Backend endpoint: POST /api/drivers/logout/ - revokes every token of this driver (bot and panel)
    url = f"{API_BASE_URL}/api/drivers/logout/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                # 401 - the token was already revoked or expired, which is fine for a logout
                return response.status in (200, 401)
    except Exception as e:
        logger.error(f"Logout API error: {e}")
        return False
