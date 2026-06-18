from django.contrib import admin

from .models import OrderDispatch


@admin.register(OrderDispatch)
class OrderDispatchAdmin(admin.ModelAdmin):
    list_display = ['order', 'driver', 'distance_to_client_km', 'is_sent', 'is_viewed', 'is_accepted', 'is_rejected', 'sent_at', 'expires_at']
    list_filter = ['is_sent', 'is_viewed', 'is_accepted', 'is_rejected', 'sent_at', 'expires_at']
    search_fields = ['order__order_number', 'driver__full_name']
    readonly_fields = ['sent_at', 'viewed_at', 'responded_at', 'expires_at']
    list_editable = ['is_accepted', 'is_rejected']
