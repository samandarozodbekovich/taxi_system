from django.db.models import F

from apps.drivers.models import Driver


def revoke_driver_tokens(driver_ids):
    """End every session (bot and panel) of these drivers - their tokens stop working at once."""
    return Driver.objects.filter(id__in=driver_ids).update(token_version=F("token_version") + 1)
