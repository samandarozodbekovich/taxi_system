import httpx

from loader import API_HEADERS, API_URL


async def register_client(data: dict):
    async with httpx.AsyncClient(headers=API_HEADERS) as client:
        try:
            response = await client.post(f"{API_URL}/api/clients/register/", json=data)
        except Exception:
            return False
    return response.status_code == 201
