from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point

# A client may have only one order in these statuses at a time (Order.Meta.constraints)
ACTIVE_ORDER_STATUSES = ('SEARCHING', 'ACCEPTED', 'WAITING', 'IN_PROGRESS')


class Order(models.Model):
    STATUS_CHOICES = (
        ('SEARCHING', 'Searching'),   # Looking for a driver
        ('ACCEPTED', 'Accepted'),     # Driver accepted
        ('WAITING', 'Waiting'),       # Driver is waiting for the client
        ('IN_PROGRESS', 'In Progress'), # On the way
        ('COMPLETED', 'Completed'),   # Completed
        ('CANCELED', 'Canceled'),     # Canceled
        ('NO_DRIVER', 'No driver'),   # Search timed out, nobody accepted (tasks.expire_order_search)
    )

    ACTIVE_STATUSES = ACTIVE_ORDER_STATUSES
    # Statuses in which the order is assigned to a driver
    DRIVER_ACTIVE_STATUSES = ('ACCEPTED', 'WAITING', 'IN_PROGRESS')

    # Status machine: current status -> statuses it may move to.
    # Every change goes through transition_to() - e.g. SEARCHING -> IN_PROGRESS is not allowed.
    ALLOWED_TRANSITIONS = {
        'SEARCHING':   {'ACCEPTED', 'CANCELED', 'NO_DRIVER'},
        'ACCEPTED':    {'WAITING', 'SEARCHING', 'CANCELED'},       # SEARCHING - the driver canceled
        'WAITING':     {'IN_PROGRESS', 'SEARCHING', 'CANCELED'},
        'IN_PROGRESS': {'COMPLETED', 'SEARCHING', 'CANCELED'},
        'NO_DRIVER':   {'CANCELED'},
        'COMPLETED':   set(),
        'CANCELED':    set(),
    }

    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    client = models.ForeignKey(
        'clients.Client', on_delete=models.CASCADE, related_name='orders'
    )
    driver = models.ForeignKey(
        'drivers.Driver', on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='orders'
    )

    # Location fields
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_address = models.TextField()
    
    pickup_location = gis_models.PointField(srid=4326, db_index=True)
    destination_location = gis_models.PointField(srid=4326, null=True, blank=True)

    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    destination_address = models.TextField(null=True, blank=True)

    
    # Money and distance
    distance_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    waiting_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    route_geometry = gis_models.LineStringField(null=True, blank=True, srid=4326)
    total_distance = models.FloatField(default=0)

    # Status and timestamps
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='SEARCHING', db_index=True
    )
    
    # Audit fields (for tracking)
    searching_started_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    arrived_at = models.DateTimeField(null=True, blank=True) # When the driver arrived
    started_at = models.DateTimeField(null=True, blank=True)  # When the trip started
    completed_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    # Cancellation details
    cancel_by = models.CharField(max_length=50, null=True, blank=True) # 'CLIENT' or 'DRIVER'
    cancel_reason = models.TextField(null=True, blank=True)

    client_comment = models.TextField(null=True, blank=True)
    driver_comment = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']
        constraints = [
            # There is a race between the "has an active order?" check and creation (double-clicking the button) -
            # the database itself rejects the second order
            models.UniqueConstraint(
                fields=['client'],
                condition=models.Q(status__in=ACTIVE_ORDER_STATUSES),
                name='one_active_order_per_client',
            ),
        ]

    def __str__(self):
        return f"#{self.order_number} - {self.client.full_name}"

    def can_transition_to(self, new_status):
        return new_status in self.ALLOWED_TRANSITIONS.get(self.status, set())

    def transition_to(self, new_status):
        """Change the status (without saving). Raises ValueError for a disallowed transition."""
        if not self.can_transition_to(new_status):
            raise ValueError(f"Cannot change order status from {self.status} to {new_status}.")
        self.status = new_status


    def save(self, *args, **kwargs):
        if self.pickup_latitude and self.pickup_longitude:
            self.pickup_location = Point(float(self.pickup_longitude), float(self.pickup_latitude))
        super().save(*args, **kwargs)