from django.contrib.gis.db import models as gis_models
from django.db import models
from django.contrib.gis.geos import Point

class Driver(models.Model):
    STATUS_CHOICES = (
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
        ('BUSY', 'Busy'),
    )

    driver_code = models.CharField(max_length=10, unique=True, db_index=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, db_index=True)
    telegram_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name="Telegram ID"
    )
    
    # Mashina ma'lumotlari
    car_model = models.CharField(max_length=255)
    car_color = models.CharField(max_length=100)
    car_number = models.CharField(max_length=50, db_index=True)
    photo = models.ImageField(upload_to='drivers/', null=True, blank=True)

    # Lokatsiya - DecimalField (oddiy ko'rish uchun)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # GeoDjango PointField (masofani tezkor hisoblash uchun)
    # SRID 4326 - Standart GPS koordinatalari (WGS84)
    current_location = gis_models.PointField(null=True, blank=True, srid=4326)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OFFLINE', db_index=True)
    wallet = models.DecimalField(max_digits=12, decimal_places=2, default=0) # Oldingi xatoda chiqqan 'wallet' field
    is_blocked = models.BooleanField(default=False)
    
    last_online_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Haydovchi"
        verbose_name_plural = "Haydovchilar"
        # GIS so'rovlari tez ishlashi uchun index qo'shamiz
        indexes = [
            models.Index(fields=['status', 'is_blocked']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.driver_code})"

    def save(self, *args, **kwargs):
        """
        Latitude va Longitude o'zgarganda PointField (current_location)ni 
        avtomatik yangilash uchun save metodini override qilamiz.
        """
        if self.current_latitude and self.current_longitude:
            self.current_location = Point(
                float(self.current_longitude), 
                float(self.current_latitude), 
                srid=4326
            )
        super().save(*args, **kwargs)

    def update_location(self, lat, lon):
        """Haydovchi koordinatasini yangilash uchun helper metod"""
        self.current_latitude = lat
        self.current_longitude = lon
        # save() metodi yuqoridagi mantiq asosida current_locationni ham yangilaydi
        self.save()