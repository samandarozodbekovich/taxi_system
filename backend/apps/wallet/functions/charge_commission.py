from apps.wallet.models import DriverWallet, WalletTransaction


def charge_commission(order, amount):
    """Deduct the order commission from the driver's wallet and log it (call inside transaction.atomic())."""
    # Row lock: concurrent balance changes can't overwrite each other
    wallet, _ = DriverWallet.objects.select_for_update().get_or_create(driver_id=order.driver_id)
    before_balance = wallet.balance
    wallet.balance -= amount
    wallet.total_commission_paid += amount
    # The client pays the driver in cash - the driver keeps the fare minus the commission
    wallet.total_earned += order.total_price - amount
    wallet.save(update_fields=['balance', 'total_commission_paid', 'total_earned', 'updated_at'])
    WalletTransaction.objects.create(
        wallet=wallet,
        order=order,
        amount=amount,
        transaction_type='COMMISSION',
        before_balance=before_balance,
        after_balance=wallet.balance,
    )
