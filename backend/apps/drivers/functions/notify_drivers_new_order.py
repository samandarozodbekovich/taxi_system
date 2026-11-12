import logging
import time

import requests
from django.conf import settings

from apps.dispatch.models import OrderDispatch
from apps.drivers.models import Driver

from .new_order_message import new_order_message

logger = logging.getLogger(__name__)

# Telegram bot limit is ~30 messages/second - send a bit slower than that
TELEGRAM_SEND_INTERVAL_SECONDS = 1 / 25


def notify_drivers_new_order(order, drivers=None):
    """
    Telegram message about a new order (called from the dispatch_new_order Celery task).
    drivers - the nearest dispatched drivers; if none, all ONLINE drivers except
    those who rejected this order.
    """
    if not drivers:
        drivers = Driver.objects.filter(
            status='ONLINE', is_blocked=False, is_approved=True, telegram_id__isnull=False
        ).exclude(id__in=OrderDispatch.objects.filter(order=order, is_rejected=True).values('driver_id'))
    drivers = [d for d in drivers if d.telegram_id]
    if not drivers:
        logger.warning(f"Order #{order.id}: no online drivers!")
        return

    text, keyboard = new_order_message(order)
    url = f"https://api.telegram.org/bot{settings.DRIVER_BOT_TOKEN}/sendMessage"
    with requests.Session() as session:
        for driver in drivers:
            payload = {"chat_id": driver.telegram_id, "text": text, "parse_mode": "HTML", "reply_markup": keyboard}
            try:
                response = session.post(url, json=payload, timeout=5)
                if response.status_code == 429:
                    # Rate limited - wait as long as Telegram says and retry once
                    time.sleep(min(response.json().get("parameters", {}).get("retry_after", 1), 30))
                    session.post(url, json=payload, timeout=5)
            except Exception as e:
                logger.error(f"Failed to send message to driver {driver.id}: {e}")
            time.sleep(TELEGRAM_SEND_INTERVAL_SECONDS)
