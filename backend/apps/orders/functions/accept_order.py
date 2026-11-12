from django.db import transaction
from django.utils import timezone

from apps.dispatch.models import OrderDispatch
from apps.drivers.models import Driver

from .get_locked_order import get_locked_order
from .is_offered_to_driver import is_offered_to_driver
from .notify_order_update import notify_order_update


def accept_order(order_id, driver):
    with transaction.atomic():
        order = get_locked_order(order_id)
        if not order.can_transition_to("ACCEPTED"):
            raise ValueError("The order is no longer available: it was accepted, canceled, or the search timed out.")
        # Only a driver the order was offered to may take it (no enumerating order ids)
        if not is_offered_to_driver(order, driver):
            raise ValueError("This order was not offered to you.")

        # request.user may be stale - re-read it under a lock so one driver can't accept two orders at once
        driver = Driver.objects.select_for_update().get(id=driver.id)
        if driver.is_blocked:
            raise ValueError("Your account is blocked.")
        if not driver.is_approved:
            raise ValueError("Your account has not been approved yet.")
        if driver.status == "BUSY":
            raise ValueError("You already have an active order.")

        order.driver = driver
        order.transition_to("ACCEPTED")
        order.accepted_at = timezone.now()
        order.save()

        driver.status = "BUSY"
        driver.save(update_fields=['status', 'updated_at'])

        now = timezone.now()
        OrderDispatch.objects.filter(order=order).exclude(driver=driver).update(
            is_accepted=False, is_rejected=True, responded_at=now
        )
        OrderDispatch.objects.filter(order=order, driver=driver).update(
            is_accepted=True, is_rejected=False, responded_at=now
        )

        notify_order_update(order.id, {
            'status': 'ACCEPTED',
            'driver_name': driver.full_name,
            'car_model': driver.car_model,
            'car_number': driver.car_number,
            'driver_phone': driver.phone_number,
        })
        return order
