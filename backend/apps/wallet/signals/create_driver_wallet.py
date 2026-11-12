from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.drivers.models import Driver
from apps.wallet.models import DriverWallet


@receiver(post_save, sender=Driver)
def create_driver_wallet(sender, instance, created, **kwargs):
    """Every driver gets a wallet, however they were created (bot, API, admin)."""
    if created:
        DriverWallet.objects.get_or_create(driver=instance)
