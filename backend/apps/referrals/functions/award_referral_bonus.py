from decimal import Decimal

from django.db.models import F

from apps.clients.models import Client
from apps.referrals.models import ReferralBonus
from apps.settings_app.models import SystemSetting

# Configurable from the admin panel: SystemSetting REFERRAL_BONUS
DEFAULT_REFERRAL_BONUS = 5000


def award_referral_bonus(order):
    """
    After the invited client's first completed trip, credit the inviter's bonus_balance
    (call inside transaction.atomic()). Returns the ReferralBonus or None.
    """
    client = order.client
    if not client.referred_by_id or ReferralBonus.objects.filter(referred=client).exists():
        return None

    amount = Decimal(SystemSetting.get_setting("REFERRAL_BONUS", DEFAULT_REFERRAL_BONUS))
    bonus = ReferralBonus.objects.create(referrer_id=client.referred_by_id, referred=client, order=order, amount=amount)
    Client.objects.filter(id=client.referred_by_id).update(bonus_balance=F('bonus_balance') + amount)
    return bonus
