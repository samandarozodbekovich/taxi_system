from django.db import transaction as db_transaction

from apps.wallet.models import DriverWallet

# How each manual transaction type changes the balance, and which statistic it adds to
BALANCE_SIGN = {'TOPUP': 1, 'ORDER_EARN': 1, 'PENALTY': -1}
STAT_FIELDS = {'ORDER_EARN': 'total_earned', 'PENALTY': 'total_penalty_paid'}


def apply_wallet_transaction(wallet_transaction):
    """
    Apply a new TOPUP / PENALTY / ORDER_EARN transaction (e.g. added by an admin) to the
    wallet balance and save it with before/after balances. Commissions use charge_commission.
    """
    if wallet_transaction.transaction_type not in BALANCE_SIGN:
        raise ValueError(f"{wallet_transaction.transaction_type} can't be added manually.")
    if wallet_transaction.amount <= 0:
        raise ValueError("The amount must be positive.")

    with db_transaction.atomic():
        wallet = DriverWallet.objects.select_for_update().get(id=wallet_transaction.wallet_id)
        wallet_transaction.before_balance = wallet.balance
        wallet.balance += BALANCE_SIGN[wallet_transaction.transaction_type] * wallet_transaction.amount
        updated_fields = ['balance', 'updated_at']

        stat_field = STAT_FIELDS.get(wallet_transaction.transaction_type)
        if stat_field:
            setattr(wallet, stat_field, getattr(wallet, stat_field) + wallet_transaction.amount)
            updated_fields.append(stat_field)
        wallet.save(update_fields=updated_fields)

        wallet_transaction.after_balance = wallet.balance
        wallet_transaction.save()
    return wallet_transaction
