from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.drivers.models import Driver
from apps.settings_app.models import SystemSetting
from apps.wallet.functions import charge_commission

from .get_locked_order import get_locked_order
from .notify_order_update import notify_order_update


def complete_order(order_id, driver):
    with transaction.atomic():
        order = get_locked_order(order_id)
        if order.driver_id is None or order.driver_id != driver.id:
            raise ValueError("This order does not belong to you.")

        order.transition_to("COMPLETED")
        order.total_price = order.estimated_price + order.waiting_price
        order.completed_at = timezone.now()
        commission_percent = Decimal(SystemSetting.get_setting("COMMISSION_PERCENT", 10))
        order.commission_amount = order.total_price * commission_percent / Decimal(100)
        order.save()

        Driver.objects.filter(id=order.driver_id).update(status="ONLINE", updated_at=timezone.now())
        charge_commission(order, order.commission_amount)

        notify_order_update(order.id, {'status': 'COMPLETED'})
        return order
