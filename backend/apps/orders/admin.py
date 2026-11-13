from django.contrib import admin

from .forms import OrderAdminForm
from .functions import cancel_by_operator, complete_order, completed_orders_summary
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ['id', 'order_number', 'status', 'total_price', 'created_at']
    # No list_editable for status: the changelist form would bypass OrderAdminForm.clean_status
    # Map fields are excluded to avoid GDAL errors
    exclude = ['pickup_location', 'destination_location', 'route_geometry']
    # Changing the driver by hand would leave the old one BUSY and the new one free
    readonly_fields = ['driver', 'dispatch_wave']

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        if hasattr(response, 'context_data') and 'cl' in response.context_data:
            response.context_data['summary_data'] = completed_orders_summary(response.context_data['cl'].queryset)
        return response

    def save_model(self, request, obj, form, change):
        new_status = obj.status
        status_changed = change and 'status' in form.changed_data
        if status_changed:
            # Save the other edits first, then change the status through the same functions the
            # apps use - so completing charges the commission and canceling frees the driver
            obj.status = form.initial['status']
        super().save_model(request, obj, form, change)

        if status_changed:
            if new_status == 'COMPLETED':
                complete_order(obj.id, obj.driver)
            elif new_status == 'CANCELED':
                cancel_by_operator(obj.id, obj.cancel_reason)
            obj.refresh_from_db()
