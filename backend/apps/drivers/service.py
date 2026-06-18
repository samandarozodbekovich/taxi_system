import logging
import requests
from django.conf import settings

from .models import Driver

logger = logging.getLogger(__name__)

def notify_drivers_new_order(order):
    """
    Yangi order yaratilganda barcha ONLINE driverlarga
    Telegram bot orqali xabar yuboradi.
    """
    drivers = Driver.objects.filter(
        status='ONLINE',
        is_blocked=False,
        telegram_id__isnull=False
    )

    if not drivers.exists():
        logger.warning(f"Order #{order.id} — online driver yo'q!")
        return

    bot_token = settings.DRIVER_BOT_TOKEN
    webapp_url = f"{settings.DRIVER_WEBAPP_URL}?order_id={order.id}"

    text = (
        f"🚖 <b>Yangi buyurtma!</b>\n\n"
        f"📍 <b>Qayerdan:</b> {order.pickup_address}\n"
        f"🏁 <b>Qayerga:</b> {order.destination_address}\n"
        f"📏 <b>Masofa:</b> {order.distance_km:.1f} km\n"
        f"💵 <b>Narx:</b> {int(order.estimated_price):,} so'm"
    )

    keyboard = {
        "inline_keyboard": [[
            {
                "text": "🚗 Panelni ochish",
                "web_app": {"url": webapp_url}
            }
        ]]
    }

    for driver in drivers:
        try:
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={
                    "chat_id": driver.telegram_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "reply_markup": keyboard
                },
                timeout=5
            )
        except Exception as e:
            logger.error(f"Driver {driver.id} ga xabar yuborishda xato: {e}")