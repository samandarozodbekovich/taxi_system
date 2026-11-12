from django.db import models
from django.core.cache import cache

class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True, 
        help_text="Setting key (e.g. MIN_PRICE, COMMISSION_PERCENT)"
        )
    value = models.CharField(max_length=255, 
        help_text="Setting value (as text)"
    )
    description = models.TextField(null=True, blank=True, 
        help_text="What this setting controls"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System setting"
        verbose_name_plural = "System settings"

    def __str__(self):
        return f"{self.key}: {self.value}"

    def save(self, *args, **kwargs):
        # Clear the cache when a setting is updated
        cache.delete(f"system_setting_{self.key}")
        super().save(*args, **kwargs)

    @classmethod
    def get_setting(cls, key, default=None):
        """Fast lookup of a setting from the cache or the database."""
        cache_key = f"system_setting_{key}"
        cached_value = cache.get(cache_key)
        
        if cached_value is not None:
            return cached_value
        
        try:
            setting = cls.objects.get(key=key)
            cache.set(cache_key, setting.value, timeout=86400) # cache for 24 hours
            return setting.value
        except cls.DoesNotExist:
            return default