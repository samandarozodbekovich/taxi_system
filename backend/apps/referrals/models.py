from django.db import models


class ReferralBonus(models.Model):
    """A bonus paid to a client for inviting a friend - at most once per invited client."""
    referrer = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='referral_bonuses')
    # OneToOne: the database itself prevents paying twice for the same invited client
    referred = models.OneToOneField('clients.Client', on_delete=models.CASCADE, related_name='referral_bonus_paid')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Referral bonus"
        verbose_name_plural = "Referral bonuses"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.referrer} invited {self.referred}: {self.amount}"
