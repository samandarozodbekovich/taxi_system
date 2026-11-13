import json
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.drivers.functions import DRIVER_TOKEN_COOKIE
from apps.orders.functions import is_order_participant, order_snapshot


class OrderConsumer(AsyncWebsocketConsumer):
    """
    Order updates (status, driver name, car plate, phone). Only the order owner
    (client - ?tma=<initData>) or the assigned driver (login token in the HttpOnly
    driver_token cookie - not in the URL, where proxies and logs would keep it) may connect.
    """

    async def connect(self):
        self.order_id = int(self.scope['url_route']['kwargs']['order_id'])
        self.order_group_name = f'order_{self.order_id}'

        params = parse_qs(self.scope.get('query_string', b'').decode())
        self.init_data = params.get('tma', [None])[0]
        # scope['cookies'] comes from CookieMiddleware (part of AuthMiddlewareStack in asgi.py)
        self.driver_token = None if self.init_data else self.scope.get('cookies', {}).get(DRIVER_TOKEN_COOKIE)
        allowed = await database_sync_to_async(is_order_participant)(self.order_id, self.init_data, self.driver_token)
        if not allowed:
            # close() before accept() rejects the handshake with 403
            await self.close()
            return

        await self.channel_layer.group_add(self.order_group_name, self.channel_name)
        await self.accept()

        # Events sent while the socket was down are lost - start from the current state
        snapshot = await database_sync_to_async(order_snapshot)(self.order_id)
        if snapshot:
            await self.send(text_data=json.dumps({'order_data': snapshot}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.order_group_name, self.channel_name)

    async def order_update(self, event):
        await self.send(text_data=json.dumps({'order_data': event['data']}))

        # A driver who is no longer assigned (dropped the order, client canceled) has just
        # got the event that says so - after that they must not see this order any more
        if self.driver_token and 'status' in event['data']:
            still_assigned = await database_sync_to_async(is_order_participant)(
                self.order_id, None, self.driver_token
            )
            if not still_assigned:
                await self.close()
