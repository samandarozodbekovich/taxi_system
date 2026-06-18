from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point

class Order(models.Model):
    STATUS_CHOICES = (
        ('SEARCHING', 'Searching'),   # Haydovchi qidirilmoqda
        ('ACCEPTED', 'Accepted'),     # Haydovchi qabul qildi
        ('WAITING', 'Waiting'),       # Haydovchi mijozni kutmoqda
        ('IN_PROGRESS', 'In Progress'), # Yo'lda
        ('COMPLETED', 'Completed'),   # Tugatildi
        ('CANCELED', 'Canceled'),     # Bekor qilindi
    )

    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    client = models.ForeignKey(
        'clients.Client', on_delete=models.CASCADE, related_name='orders'
    )
    driver = models.ForeignKey(
        'drivers.Driver', on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='orders'
    )

    # Lokatsiya maydonlari
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_address = models.TextField()
    
    pickup_location = gis_models.PointField(srid=4326, db_index=True)
    destination_location = gis_models.PointField(srid=4326, null=True, blank=True)

    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    destination_address = models.TextField(null=True, blank=True)

    
    # Moliyaviy va Masofa ma'lumotlari
    distance_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    waiting_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    route_geometry = gis_models.LineStringField(null=True, blank=True, srid=4326)
    total_distance = models.FloatField(default=0)

    # Status va Vaqtlar
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='SEARCHING', db_index=True
    )
    
    # Audit maydonlari (Track qilish uchun)
    searching_started_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    arrived_at = models.DateTimeField(null=True, blank=True) # Haydovchi yetib kelgan vaqt
    started_at = models.DateTimeField(null=True, blank=True)  # Safar boshlangan vaqt
    completed_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    # Bekor qilish sabablari
    cancel_by = models.CharField(max_length=50, null=True, blank=True) # 'CLIENT' yoki 'DRIVER'
    cancel_reason = models.TextField(null=True, blank=True)

    client_comment = models.TextField(null=True, blank=True)
    driver_comment = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.order_number} - {self.client.full_name}"


    def save(self, *args, **kwargs):
        if self.pickup_latitude and self.pickup_longitude:
            self.pickup_location = Point(float(self.pickup_longitude), float(self.pickup_latitude))
        super().save(*args, **kwargs)