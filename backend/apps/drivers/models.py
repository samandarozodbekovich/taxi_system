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
    # Part of every login token; incrementing it ends all of the driver's sessions
    # (logout, password change, admin action) - see create_driver_token / driver_from_token
    token_version = models.PositiveIntegerField(default=0)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, db_index=True)
    telegram_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name="Telegram ID"
    )
    
    # Car details
    car_model = models.CharField(max_length=255)
    car_color = models.CharField(max_length=100)
    car_number = models.CharField(max_length=50, db_index=True)
    photo = models.ImageField(upload_to='drivers/', null=True, blank=True)

    # Location - DecimalField (for easy viewing)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # GeoDjango PointField (for fast distance calculations)
    # SRID 4326 - standard GPS coordinates (WGS84)
    # geography: distances are in metres on the sphere, and the GiST index serves
    # "drivers within N km" (ST_DWithin) - the dispatch search
    current_location = gis_models.PointField(null=True, blank=True, srid=4326, geography=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OFFLINE', db_index=True)
    is_blocked = models.BooleanField(default=False)
    # A new driver cannot log in or receive orders until an admin reviews the documents and approves them
    is_approved = models.BooleanField(default=False, verbose_name="Approved")
    
    last_online_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Driver"
        verbose_name_plural = "Drivers"
        # Index so GIS queries run fast
        indexes = [
            models.Index(fields=['status', 'is_blocked']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.driver_code})"

    # Needed when used as DRF request.user (DriverTokenAuthentication).
    # These are plain properties, not DB fields - no migration required.
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def save(self, *args, **kwargs):
        """
        Override save so the PointField (current_location) is updated automatically
        when latitude and longitude change.
        """
        if self.current_latitude and self.current_longitude:
            self.current_location = Point(
                float(self.current_longitude), 
                float(self.current_latitude), 
                srid=4326
            )
        super().save(*args, **kwargs)

    def update_location(self, lat, lon):
        """Helper to update the driver's coordinates."""
        self.current_latitude = lat
        self.current_longitude = lon
        # save() also updates current_location using the logic above.
        # Only the location fields are written: the GPS request every 5 seconds must not overwrite
        # status='BUSY' from a concurrent accept_order with a stale value
        self.save(update_fields=['current_latitude', 'current_longitude', 'current_location', 'updated_at'])