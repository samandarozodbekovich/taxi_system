from django.contrib import admin

from .models import DriverWallet, WalletTransaction


@admin.register(DriverWallet)
class DriverWalletAdmin(admin.ModelAdmin):
    list_display = ['driver', 'balance', 'total_earned', 'total_commission_paid', 'total_penalty_paid', 'can_accept_order', 'updated_at']
    search_fields = ['driver__full_name', 'driver__driver_code']
    readonly_fields = ['updated_at', 'can_accept_order']


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'order', 'transaction_type', 'amount', 'before_balance', 'after_balance', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['wallet__driver__full_name', 'wallet__driver__driver_code', 'note']
    readonly_fields = ['created_at']
