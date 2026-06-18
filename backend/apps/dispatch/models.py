from django.db import models
from django.utils import timezone

class OrderDispatch(models.Model):
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.CASCADE, 
        related_name='dispatches'
    )
    driver = models.ForeignKey(
        'drivers.Driver', 
        on_delete=models.CASCADE, 
        related_name='dispatches'
    )

    # Masofani saqlash (bu haydovchining buyurtma berilgan vaqtdagi masofasi)
    distance_to_client_km = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    
    # Statuslar
    is_sent = models.BooleanField(default=True) # Yaratildimi, demak yuborildi
    is_viewed = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    
    # Vaqtlar
    sent_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Timeout uchun (Masalan, 30 soniya ichida javob bermasa, keyingi driverga o'tadi)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Buyurtma taqsimoti"
        verbose_name_plural = "Buyurtma taqsimotlari"
        # Bitta haydovchiga bitta buyurtma bir marta yuborilishi shart
        unique_together = ('order', 'driver')
        indexes = [
            models.Index(fields=['order', 'is_accepted']),
        ]

    def __str__(self):
        return f"Order #{self.order.id} -> Driver: {self.driver.full_name}"

    def accept(self):
        """Haydovchi qabul qilganda chaqiriladi"""
        self.is_accepted = True
        self.responded_at = timezone.now()
        self.save()

    def reject(self):
        """Haydovchi rad etganda chaqiriladi"""
        self.is_rejected = True
        self.responded_at = timezone.now()
        self.save()