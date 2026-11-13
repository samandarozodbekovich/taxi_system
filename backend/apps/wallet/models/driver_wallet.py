from django.db import models

# Lowest balance at which a driver still gets and may accept offers. Commission is charged
# after the trip, so a new driver at 0 can work and the balance may go below 0 after a trip.
# Used by DriverWallet.can_accept_order, the dispatch filters and accept_order.
MIN_BALANCE_TO_ACCEPT_ORDERS = 0

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
        """Can the driver accept orders? (Same rule as the dispatch filters)"""
        return self.balance >= MIN_BALANCE_TO_ACCEPT_ORDERS