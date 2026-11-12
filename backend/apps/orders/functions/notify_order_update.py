from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction


def notify_order_update(order_id, data):
    """
    Push a status change to the client (TMA) over WebSocket.

    Sent only after the transaction commits, so a rolled-back change is never shown.
    Outside a transaction it is sent immediately. robust=True: if Redis is down the
    error is logged, but a committed request doesn't return 500.
    """
    def send():
        async_to_sync(get_channel_layer().group_send)(
            f'order_{order_id}',
            {'type': 'order_update', 'data': data}
        )

    transaction.on_commit(send, robust=True)
