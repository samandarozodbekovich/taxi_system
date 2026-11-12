from django.test import TestCase, override_settings

from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import make_driver
from apps.orders.functions import dispatch_order_to_all_online

from .functions import make_client, make_dispatch, make_order


@override_settings(CACHES=LOCMEM_CACHE)
class DispatchOrderToAllOnlineTests(TestCase):
    """Fallback dispatch: drivers notified on Telegram must get a dispatch, or they couldn't accept."""

    def test_offers_only_eligible_drivers_not_offered_yet(self):
        order = make_order(make_client(6001))
        online = make_driver("DRV-AAAAA1", status="ONLINE", telegram_id=111)
        make_driver("DRV-BBBBB2", status="OFFLINE", telegram_id=222)
        make_driver("DRV-CCCCC3", status="ONLINE", telegram_id=None)
        already = make_driver("DRV-DDDDD4", status="ONLINE", telegram_id=444)
        make_dispatch(order, already)

        dispatches = dispatch_order_to_all_online(order)

        self.assertEqual([d.driver_id for d in dispatches], [online.id])
