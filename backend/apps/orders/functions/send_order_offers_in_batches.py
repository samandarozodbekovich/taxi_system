from apps.orders.tasks import send_order_offers

# Telegram allows ~30 messages/second per bot: one batch is about one second of sending
TELEGRAM_BATCH_SIZE = 25


def send_order_offers_in_batches(order_id, driver_ids):
    """
    Send the offer to the drivers on Telegram. The first batch (the nearest drivers - a normal
    wave fits in it) is sent right away; the rest of a large broadcast goes to separate Celery
    tasks one second apart, so the dispatch task isn't busy for a minute and the rate limit holds.
    """
    batches = [driver_ids[i:i + TELEGRAM_BATCH_SIZE] for i in range(0, len(driver_ids), TELEGRAM_BATCH_SIZE)]
    if not batches:
        return
    send_order_offers(order_id, batches[0])
    for delay_seconds, batch in enumerate(batches[1:], start=1):
        send_order_offers.apply_async(args=[order_id, batch], countdown=delay_seconds)
