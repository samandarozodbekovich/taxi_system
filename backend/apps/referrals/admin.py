from django.contrib import admin

from .models import ReferralBonus


@admin.register(ReferralBonus)
class ReferralBonusAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referred', 'amount', 'order', 'created_at']
    search_fields = ['referrer__full_name', 'referrer__phone_number', 'referred__full_name', 'referred__phone_number']
    readonly_fields = ['referrer', 'referred', 'order', 'amount', 'created_at']
