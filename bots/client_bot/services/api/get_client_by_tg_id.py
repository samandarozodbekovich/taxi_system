import httpx

from loader import API_HEADERS, API_URL


async def get_client_by_tg_id(telegram_id: int):
    async with httpx.AsyncClient(headers=API_HEADERS) as client:
        try:
            response = await client.get(f"{API_URL}/api/clients/check/{telegram_id}/")
        except Exception:
            return None
    return response.json() if response.status_code == 200 else None
