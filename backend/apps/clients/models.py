from django.db import models
from django.utils import timezone
import uuid

class Client(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, db_index=True)
    additional_phone = models.CharField(max_length=20, null=True, blank=True)
    language_code = models.CharField(max_length=10, default='uz')
    referral_code = models.CharField(max_length=20, unique=True, db_index=True)
    referred_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='referrals'
    )
    bonus_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Block system
    is_blocked = models.BooleanField(default=False)
    blocked_until = models.DateTimeField(null=True, blank=True)
    block_reason = models.TextField(null=True, blank=True)
    
    last_order_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"

    # Needed when used as DRF request.user (apps.clients.authentication).
    # These are plain properties, not DB fields - no migration required.
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_currently_blocked(self):
        """Whether the client is blocked, taking blocked_until into account."""
        if not self.is_blocked:
            return False
        # No blocked_until means an indefinite block (previously this case was treated as "not blocked")
        if self.blocked_until is None:
            return True
        return self.blocked_until > timezone.now()

    def save(self, *args, **kwargs):
        # Generate a referral code (if missing)
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)