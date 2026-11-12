from django.contrib import admin

from .forms import WalletTransactionAdminForm
from .functions import apply_wallet_transaction
from .models import DriverWallet, WalletTransaction


@admin.register(DriverWallet)
class DriverWalletAdmin(admin.ModelAdmin):
    list_display = ['driver', 'balance', 'total_earned', 'total_commission_paid', 'total_penalty_paid', 'can_accept_order', 'updated_at']
    search_fields = ['driver__full_name', 'driver__driver_code']
    # The balance changes only through wallet transactions, so every change is logged
    readonly_fields = ['balance', 'total_earned', 'total_commission_paid', 'total_penalty_paid', 'updated_at', 'can_accept_order']


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    form = WalletTransactionAdminForm
    list_display = ['wallet', 'order', 'transaction_type', 'amount', 'before_balance', 'after_balance', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['wallet__driver__full_name', 'wallet__driver__driver_code', 'note']

    def get_readonly_fields(self, request, obj=None):
        # Saved transactions are an audit log - view only
        if obj:
            return ['wallet', 'order', 'transaction_type', 'amount', 'before_balance', 'after_balance', 'note', 'created_at']
        return []

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change:
            apply_wallet_transaction(obj)
