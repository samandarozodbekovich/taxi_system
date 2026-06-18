from django.db import models
from .driver_wallet import DriverWallet

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('COMMISSION', 'Komissiya yechildi'),
        ('PENALTY', 'Jarima yechildi'),
        ('TOPUP', 'Balans to‘ldirildi (Admin)'),
        ('ORDER_EARN', 'Buyurtmadan tushum'), # Agar naqd pulsiz bo'lsa
    )

    wallet = models.ForeignKey(
        DriverWallet, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    # Tranzaksiyadan oldingi va keyingi holat (Audit uchun juda muhim)
    before_balance = models.DecimalField(max_digits=12, decimal_places=2)
    after_balance = models.DecimalField(max_digits=12, decimal_places=2)
    
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Hamyon operatsiyasi"
        verbose_name_plural = "Hamyon operatsiyalari"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type}: {self.amount}"