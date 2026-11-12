from django.contrib import admin

from .models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'driver_code', 'phone_number', 'car_number', 'status', 'is_approved', 'is_blocked', 'current_latitude', 'current_longitude', 'created_at']
    list_filter = ['is_approved', 'status', 'is_blocked', 'created_at']
    list_editable = ['is_approved']
    actions = ['approve_drivers']
    search_fields = ['full_name', 'driver_code', 'phone_number', 'car_number']
    readonly_fields = ['driver_code', 'created_at', 'updated_at', 'current_latitude', 'current_longitude']

    @admin.action(description="Approve selected drivers")
    def approve_drivers(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} driver(s) approved.")
