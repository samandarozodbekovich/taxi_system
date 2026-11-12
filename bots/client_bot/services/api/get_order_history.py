import httpx

from loader import API_HEADERS, API_URL


async def get_order_history(telegram_id: int):
    """List of the client's latest orders, or None on error."""
    async with httpx.AsyncClient(headers=API_HEADERS) as client:
        try:
            response = await client.get(f"{API_URL}/api/orders/history/", params={"client_telegram_id": telegram_id})
        except Exception:
            return None
    return response.json() if response.status_code == 200 else None
