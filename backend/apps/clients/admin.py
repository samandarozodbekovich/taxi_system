from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone_number', 'telegram_id', 'is_blocked', 'bonus_balance', 'created_at', 'is_currently_blocked']
    list_filter = ['is_blocked', 'language_code', 'created_at']
    search_fields = ['full_name', 'phone_number', 'telegram_id', 'username', 'referral_code']
    readonly_fields = ['telegram_id', 'referral_code', 'created_at', 'updated_at', 'is_currently_blocked']
    list_editable = ['is_blocked']
