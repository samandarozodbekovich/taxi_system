from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.test import TransactionTestCase, override_settings

from apps.drivers.functions import DRIVER_TOKEN_COOKIE, create_driver_token
from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import make_driver
from apps.orders.models import Order

from config.asgi import application

from .functions import make_client, make_order

IN_MEMORY_LAYER = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}


@override_settings(CACHES=LOCMEM_CACHE, CHANNEL_LAYERS=IN_MEMORY_LAYER)
class OrderConsumerTests(TransactionTestCase):
    """The order WebSocket: current state on connect, and a dropped driver is disconnected."""

    def setUp(self):
        self.driver = make_driver("DRV-AAAAA1", status="BUSY")
        self.order = make_order(make_client(9101), "ACCEPTED", self.driver)

    def connect_driver(self, origin=None, token=None):
        # The full ASGI app (origin check + cookie middleware), as the browser panel connects
        token = token or create_driver_token(self.driver)
        origin = origin or f"http://{settings.ALLOWED_HOSTS[0]}"
        headers = [(b"origin", origin.encode()), (b"cookie", f"{DRIVER_TOKEN_COOKIE}={token}".encode())]
        return WebsocketCommunicator(application, f"/ws/order/{self.order.id}/", headers=headers)

    def test_other_site_cannot_connect_with_drivers_cookie(self):
        async def scenario():
            connected, _ = await self.connect_driver(origin="https://evil.example").connect()
            self.assertFalse(connected)

        async_to_sync(scenario)()

    def test_token_in_url_is_not_accepted(self):
        async def scenario():
            ws = WebsocketCommunicator(
                application, f"/ws/order/{self.order.id}/?token={create_driver_token(self.driver)}",
                headers=[(b"origin", f"http://{settings.ALLOWED_HOSTS[0]}".encode())],
            )
            connected, _ = await ws.connect()
            self.assertFalse(connected)

        async_to_sync(scenario)()

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
