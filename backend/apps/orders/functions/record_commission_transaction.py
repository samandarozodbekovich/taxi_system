import logging

from apps.wallet.models import DriverWallet, WalletTransaction

logger = logging.getLogger(__name__)


def record_commission_transaction(order, commission_amount):
    """Charge the commission from the driver's DriverWallet and log a WalletTransaction (if the wallet exists)."""
    try:
        wallet = DriverWallet.objects.select_for_update().get(driver_id=order.driver_id)
    except DriverWallet.DoesNotExist:
        logger.warning(f"Order {order.id}: driver {order.driver_id} has no DriverWallet")
        return

    before_balance = wallet.balance
    wallet.balance -= commission_amount
    wallet.total_commission_paid += commission_amount
    wallet.save()
    WalletTransaction.objects.create(
        wallet=wallet,
        order=order,
        amount=commission_amount,
        transaction_type='COMMISSION',
        before_balance=before_balance,
        after_balance=wallet.balance,
    )
