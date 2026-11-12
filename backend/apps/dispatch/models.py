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

    # Stored distance (the driver's distance to the client when the order was offered)
    distance_to_client_km = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    
    # Statuses
    is_sent = models.BooleanField(default=True) # Created means sent
    is_viewed = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    
    # Timestamps
    sent_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # For timeouts (e.g. if the driver does not answer in time, the next driver gets the offer)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Order dispatch"
        verbose_name_plural = "Order dispatches"
        # An order is offered to a given driver only once
        unique_together = ('order', 'driver')
        indexes = [
            models.Index(fields=['order', 'is_accepted']),
        ]

    def __str__(self):
        return f"Order #{self.order.id} -> Driver: {self.driver.full_name}"

    def accept(self):
        """Called when the driver accepts."""
        self.is_accepted = True
        self.responded_at = timezone.now()
        self.save()

    def reject(self):
        """Called when the driver rejects."""
        self.is_rejected = True
        self.responded_at = timezone.now()
        self.save()