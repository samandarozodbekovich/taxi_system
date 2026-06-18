from django.db import models

class DriverWallet(models.Model):
    driver = models.OneToOneField(
        'drivers.Driver', 
        on_delete=models.CASCADE, 
        related_name='wallet_record'
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Statistika uchun (Agregatsiya qilishni osonlashtiradi)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_commission_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_penalty_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Haydovchi hamyoni"
        verbose_name_plural = "Haydovchi hamyonlari"

    def __str__(self):
        return f"{self.driver.full_name} - Balans: {self.balance}"

    def can_accept_order(self):
        """Haydovchi buyurtma qabul qila oladimi? (Balans 0 dan yuqori bo'lishi shart)"""
        return self.balance > 0