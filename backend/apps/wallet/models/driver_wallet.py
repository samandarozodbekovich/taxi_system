from django.db import models

class DriverWallet(models.Model):
    driver = models.OneToOneField(
        'drivers.Driver', 
        on_delete=models.CASCADE, 
        related_name='wallet_record'
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # For statistics (makes aggregation easier)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_commission_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_penalty_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Driver wallet"
        verbose_name_plural = "Driver wallets"

    def __str__(self):
        return f"{self.driver.full_name} - Balance: {self.balance}"

    def can_accept_order(self):
        """Can the driver accept orders? (The balance must be above 0)"""
        return self.balance > 0