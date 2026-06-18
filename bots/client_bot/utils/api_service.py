import httpx
from loader import API_URL

async def get_client_by_tg_id(telegram_id: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/api/clients/check/{telegram_id}/")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

async def register_client(data: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_URL}/api/clients/register/", json=data)
            return response.status_code == 201
        except Exception:
            return False
        
async def create_taxi_order(order_data:dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_URL}/api/orders/create/", json=order_data)
            try:
                result = response.json()
            except:
                result = {"error": "server error (no json response)"}
            return result, response.status_code
            
        except Exception as e:
            print(f"order API error: {e}")
            return None, 500