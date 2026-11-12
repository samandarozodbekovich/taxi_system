import httpx

from loader import API_HEADERS, API_URL


async def get_client_bonus(telegram_id: int):
    """{"bonus_balance", "referral_code", "invited_count"} or None."""
    async with httpx.AsyncClient(headers=API_HEADERS) as client:
        try:
            response = await client.get(f"{API_URL}/api/clients/bonus/", params={"client_telegram_id": telegram_id})
        except Exception:
            return None
    return response.json() if response.status_code == 200 else None
