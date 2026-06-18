from django.db import models
from django.core.cache import cache

class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True, 
        help_text="Sozlama kaliti (masalan: MIN_PRICE, COMMISSION_PERCENT)"
        )
    value = models.CharField(max_length=255, 
        help_text="Sozlama qiymati (matn ko'rinishida)"
    )
    description = models.TextField(null=True, blank=True, 
        help_text="Ushbu sozlama nima uchun javobgar ekanligi haqida"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tizim sozlamasi"
        verbose_name_plural = "Tizim sozlamalari"

    def __str__(self):
        return f"{self.key}: {self.value}"

    def save(self, *args, **kwargs):
        # Sozlama yangilanganda keschni tozalaymiz
        cache.delete(f"system_setting_{self.key}")
        super().save(*args, **kwargs)

    @classmethod
    def get_setting(cls, key, default=None):
        """Sozlamani keshdan yoki bazadan tezkor olish uchun metod"""
        cache_key = f"system_setting_{key}"
        cached_value = cache.get(cache_key)
        
        if cached_value is not None:
            return cached_value
        
        try:
            setting = cls.objects.get(key=key)
            cache.set(cache_key, setting.value, timeout=86400) # 24 soat keshda saqlash
            return setting.value
        except cls.DoesNotExist:
            return default