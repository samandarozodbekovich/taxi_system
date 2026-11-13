from django.contrib import admin
from django.db.models import F

from .functions import revoke_driver_tokens
from .models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'driver_code', 'phone_number', 'car_number', 'status', 'is_approved', 'is_blocked', 'current_latitude', 'current_longitude', 'created_at']
    list_filter = ['is_approved', 'status', 'is_blocked', 'created_at']
    list_editable = ['is_approved']
    actions = ['approve_drivers', 'end_sessions']
    search_fields = ['full_name', 'driver_code', 'phone_number', 'car_number']
    readonly_fields = ['driver_code', 'token_version', 'created_at', 'updated_at', 'current_latitude', 'current_longitude']

    @admin.action(description="Approve selected drivers")
    def approve_drivers(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} driver(s) approved.")

    @admin.action(description="End all sessions (log out of the bot and panel)")
    def end_sessions(self, request, queryset):
        updated = revoke_driver_tokens(queryset.values_list('id', flat=True))
        self.message_user(request, f"Sessions ended for {updated} driver(s).")

    def save_model(self, request, obj, form, change):
        # A new password must log out whoever knew the old one
        if change and 'password_hash' in form.changed_data:
            obj.token_version = F('token_version') + 1
        super().save_model(request, obj, form, change)
        if not isinstance(obj.token_version, int):
            # Replace the F() expression with the saved number
            obj.refresh_from_db(fields=['token_version'])
