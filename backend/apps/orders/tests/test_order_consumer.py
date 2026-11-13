from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase, override_settings

from apps.drivers.functions import create_driver_token
from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import make_driver
from apps.orders.models import Order
from apps.orders.routing import websocket_urlpatterns

from .functions import make_client, make_order

IN_MEMORY_LAYER = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}


@override_settings(CACHES=LOCMEM_CACHE, CHANNEL_LAYERS=IN_MEMORY_LAYER)
class OrderConsumerTests(TransactionTestCase):
    """The order WebSocket: current state on connect, and a dropped driver is disconnected."""

    def setUp(self):
        self.driver = make_driver("DRV-AAAAA1", status="BUSY")
        self.order = make_order(make_client(9101), "ACCEPTED", self.driver)

    def connect_driver(self):
        token = create_driver_token(self.driver)
        return WebsocketCommunicator(URLRouter(websocket_urlpatterns), f"/ws/order/{self.order.id}/?token={token}")

    def test_snapshot_on_connect(self):
        async def scenario():
            ws = self.connect_driver()
            connected, _ = await ws.connect()
            self.assertTrue(connected)
            message = await ws.receive_json_from()
            self.assertEqual(message["order_data"]["status"], "ACCEPTED")
            self.assertEqual(message["order_data"]["car_model"], "Cobalt")
            await ws.disconnect()

        async_to_sync(scenario)()

    def test_dropped_driver_gets_the_event_then_is_disconnected(self):
        async def scenario():
            ws = self.connect_driver()
            await ws.connect()
            await ws.receive_json_from()  # snapshot

            # The order went back to searching without this driver
            await database_update(self.order.id)
            await get_channel_layer().group_send(
                f"order_{self.order.id}", {"type": "order_update", "data": {"status": "SEARCHING"}}
            )
            message = await ws.receive_json_from()
            self.assertEqual(message["order_data"]["status"], "SEARCHING")
            closed = await ws.receive_output()
            self.assertEqual(closed["type"], "websocket.close")

        async_to_sync(scenario)()


async def database_update(order_id):
    await database_sync_to_async(Order.objects.filter(id=order_id).update)(driver=None, status="SEARCHING")
