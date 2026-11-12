import html

from django.conf import settings


def new_order_message(order):
    """Telegram text and inline keyboard for a new-order notification."""
    # Addresses come from the client - escape them, parse_mode=HTML would break or allow injecting links
    text = (
        f"🚖 <b>New order!</b>\n\n"
        f"📍 <b>From:</b> {html.escape(order.pickup_address or '')}\n"
        f"🏁 <b>To:</b> {html.escape(order.destination_address or '')}\n"
        f"📏 <b>Distance:</b> {order.distance_km:.1f} km\n"
        f"💵 <b>Price:</b> {int(order.estimated_price):,} UZS"
    )
    keyboard = {"inline_keyboard": [[{
        "text": "🚗 Open panel",
        "web_app": {"url": f"{settings.DRIVER_WEBAPP_URL}?order_id={order.id}"},
    }]]}
    return text, keyboard
