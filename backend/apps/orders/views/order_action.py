import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.drivers.mixins import DriverAuthMixin
from apps.orders.functions import (
    accept_order, cancel_by_driver, complete_order, driver_update_status, reject_by_driver,
)

logger = logging.getLogger(__name__)

ACTIONS = {
    "accept": accept_order,
    "reject": reject_by_driver,
    "arrive": lambda order_id, driver: driver_update_status(order_id, driver, 'WAITING'),
    "start": lambda order_id, driver: driver_update_status(order_id, driver, 'IN_PROGRESS'),
    "complete": complete_order,
    "cancel": cancel_by_driver,
}


class OrderActionView(DriverAuthMixin, APIView):

    def post(self, request, order_id):
        action = request.data.get('action')
        if action not in ACTIONS:
            return Response({"error": "Invalid action."}, status=400)

        try:
            # The driver comes from the token, not from the request body
            ACTIONS[action](order_id, request.user)
        except ValueError as e:
            # Business rule errors (wrong status, another driver's order, etc.)
            return Response({"error": str(e)}, status=400)
        except Exception:
            logger.exception("Order action failed: order=%s action=%s", order_id, action)
            return Response({"error": "Internal server error."}, status=500)
        return Response({"message": f"Success: {action}"})
