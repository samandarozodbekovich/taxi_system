
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_sync
from apps.orders.models import OrderDispatch
from apps.orders.services import OrderService

class DriverConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.driver = getattr(self.scope["user"], 'driver_profile', self.scope["user"])
        if not getattr(self.driver, 'is_authenticated', False):
            await self.close()
            return

        self.group_name = f"driver_{self.driver.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Celery taskdan kelgan xabarni haydovchiga (frontendga) yuborish
    async def send_order_offer(self, event):
        await self.send(text_data=json.dumps({
            "action": "new_order_offer",
            "dispatch_id": event["dispatch_id"],
            "order_id": event["order_id"],
            "pickup_location": event["pickup_location"],
            "dropoff_location": event["dropoff_location"],
            "distance_to_client_km": event["distance_to_client_km"],
            "timeout_seconds": event["timeout_seconds"]
        }))

    # Haydovchi tugmalarni bosganda frontenddan keladigan xabar
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        dispatch_id = data.get("dispatch_id")

        if action == "accept_order":
            success = await self.handle_order_response(dispatch_id, accept=True)
            if success:
                await self.send(text_data=json.dumps({"status": "order_secured"}))
                # Tizimdagi boshqa qismlarga (masalan mijozga) haydovchi topilganini bildirish mumkin
        
        elif action == "reject_order":
            await self.handle_order_response(dispatch_id, accept=False)
            await self.send(text_data=json.dumps({"status": "order_rejected_acknowledged"}))

    @database_sync_to_sync
    def handle_order_response(self, dispatch_id, accept):
        """ Bazadagi holatni yangilash """
        try:
            dispatch = OrderDispatch.objects.get(id=dispatch_id)
            order = dispatch.order

            if order.status != "SEARCHING":
                return False # Buyurtma allaqachon ketgan

            if accept:
                try:
                    OrderService.accept_order(order.id, self.driver)
                except Exception:
                    return False
                return True
            else:
                dispatch.is_rejected = True
                dispatch.save()
                return False
        except OrderDispatch.DoesNotExist:
            return False