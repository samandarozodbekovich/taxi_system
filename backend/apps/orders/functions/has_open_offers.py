from django.utils import timezone

from apps.dispatch.models import OrderDispatch


def has_open_offers(order_id):
    """True while some driver can still answer the order's current wave of offers."""
    return OrderDispatch.objects.filter(
        order_id=order_id, is_accepted=False, is_rejected=False, expires_at__gt=timezone.now()
    ).exists()
