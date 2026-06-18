from django.contrib import admin

from .models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'driver_code', 'phone_number', 'status', 'is_blocked', 'current_latitude', 'current_longitude', 'created_at']
    list_filter = ['status', 'is_blocked', 'created_at']
    search_fields = ['full_name', 'driver_code', 'phone_number', 'car_number']
    readonly_fields = ['driver_code', 'created_at', 'updated_at', 'current_latitude', 'current_longitude']
