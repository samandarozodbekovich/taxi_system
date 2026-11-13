import threading
from unittest.mock import patch

from django.db import connection
from django.test import TransactionTestCase, override_settings

from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import make_driver
from apps.orders.functions import accept_order
from apps.orders.models import Order
from apps.wallet.models import DriverWallet

from .functions import make_client, make_dispatch, make_order

REJECT_MODULE = "apps.orders.functions.reject_by_driver"


def run_at_once(*calls):
    """
    Run the calls in parallel threads, each with its own database connection, released
    together by a barrier - real concurrent transactions, unlike TestCase, which runs
    everything in one transaction on one connection.
    """
    barrier = threading.Barrier(len(calls))
    results = [None] * len(calls)

    def worker(index, call):
        try:
            barrier.wait()
            results[index] = ("ok", call())
        except Exception as e:  # noqa: BLE001 - the test inspects what each thread raised
            results[index] = ("error", e)
        finally:
            connection.close()

    threads = [threading.Thread(target=worker, args=(i, c)) for i, c in enumerate(calls)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    return results


@override_settings(CACHES=LOCMEM_CACHE)
@patch("apps.orders.functions.accept_order.notify_order_update")
class ConcurrentAcceptTests(TransactionTestCase):
    """Two drivers press "Accept" at the same moment: exactly one gets the order."""

    def test_only_one_driver_wins(self, notify):
        order = make_order(make_client(9501))
        drivers = [make_driver(f"DRV-RACE0{i}", status="ONLINE") for i in (1, 2)]
        for driver in drivers:
            DriverWallet.objects.get_or_create(driver=driver)
            make_dispatch(order, driver)

        results = run_at_once(*[lambda d=d: accept_order(order.id, d) for d in drivers])

        outcomes = sorted(kind for kind, _ in results)
        self.assertEqual(outcomes, ["error", "ok"])
        errors = [value for kind, value in results if kind == "error"]
        self.assertIsInstance(errors[0], ValueError)

        order.refresh_from_db()
        winner = next(value for kind, value in results if kind == "ok")
        self.assertEqual(order.status, "ACCEPTED")
        self.assertEqual(order.driver_id, winner.driver_id)


@override_settings(CACHES=LOCMEM_CACHE)
class ConcurrentRejectTests(TransactionTestCase):
    """The last two drivers of a wave reject at once: the next wave starts exactly once."""

    def test_next_wave_is_scheduled_once(self):
        from apps.orders.functions import reject_by_driver

        order = make_order(make_client(9502))
        drivers = [make_driver(f"DRV-RJCT0{i}", status="ONLINE") for i in (1, 2)]
        for driver in drivers:
            make_dispatch(order, driver)

        # on_commit callbacks run for real here; count them instead of starting Celery
        with patch(f"{REJECT_MODULE}.schedule_dispatch") as schedule:
            results = run_at_once(*[lambda d=d: reject_by_driver(order.id, d) for d in drivers])

        self.assertEqual([kind for kind, _ in results], ["ok", "ok"])
        # Without the order lock each saw the other's offer still open, and neither scheduled it
        self.assertEqual(schedule.call_count, 1)
        self.assertEqual(Order.objects.get(id=order.id).status, "SEARCHING")
