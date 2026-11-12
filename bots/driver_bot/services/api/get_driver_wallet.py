import aiohttp
import logging
from config import API_BASE_URL

logger = logging.getLogger(__name__)


async def get_driver_wallet(token: str) -> dict:
    # Backend endpoint: GET /api/wallet/info/ - the driver is resolved from the token
    url = f"{API_BASE_URL}/api/wallet/info/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"success": True, "balance": float(data.get("balance", 0))}
                if response.status == 401:
                    return {"success": False, "message": "Session expired. Log in again: /start"}
                return {"success": False, "message": "Balance not found"}
    except Exception as e:
        logger.error(f"Wallet API error: {e}")
        return {"success": False, "message": "Cannot reach the server"}
