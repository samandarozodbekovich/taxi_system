import json
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.orders.functions import is_order_participant


class OrderConsumer(AsyncWebsocketConsumer):
    """
    Order updates (status, driver name, car plate, phone). Only the order owner
    (client - ?tma=<initData>) or the assigned driver (?token=<login token>) may connect.
    """

    async def connect(self):
        self.order_id = int(self.scope['url_route']['kwargs']['order_id'])
        self.order_group_name = f'order_{self.order_id}'

        params = parse_qs(self.scope.get('query_string', b'').decode())
        allowed = await database_sync_to_async(is_order_participant)(
            self.order_id, params.get('tma', [None])[0], params.get('token', [None])[0]
        )
        if not allowed:
            # close() before accept() rejects the handshake with 403
            await self.close()
            return

        await self.channel_layer.group_add(self.order_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.order_group_name, self.channel_name)

    async def order_update(self, event):
        await self.send(text_data=json.dumps({'order_data': event['data']}))
