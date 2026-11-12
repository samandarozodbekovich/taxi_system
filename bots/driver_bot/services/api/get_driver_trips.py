import logging

import aiohttp

from config import API_BASE_URL

logger = logging.getLogger(__name__)


async def get_driver_trips(token: str) -> dict:
    # Backend endpoint: GET /api/orders/driver/history/ - the driver is resolved from the token
    url = f"{API_BASE_URL}/api/orders/driver/history/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return {"success": True, "trips": await response.json()}
                if response.status == 401:
                    return {"success": False, "message": "Session expired. Log in again: /start"}
                return {"success": False, "message": "Could not load your trips"}
    except Exception as e:
        logger.error(f"Trips API error: {e}")
        return {"success": False, "message": "Cannot reach the server"}
