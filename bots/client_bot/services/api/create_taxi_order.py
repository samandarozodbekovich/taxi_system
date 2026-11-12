import httpx

from loader import API_HEADERS, API_URL


async def create_taxi_order(order_data: dict):
    """Returns (response_json, status_code)."""
    async with httpx.AsyncClient(headers=API_HEADERS) as client:
        try:
            response = await client.post(f"{API_URL}/api/orders/create/", json=order_data)
        except Exception as e:
            print(f"order API error: {e}")
            return {"error": "Cannot reach the server"}, 500
    try:
        return response.json(), response.status_code
    except ValueError:
        return {"error": "server error (no json response)"}, response.status_code
