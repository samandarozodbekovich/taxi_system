from django.contrib import admin

from .forms import OrderAdminForm
from .functions import completed_orders_summary, notify_order_update
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ['id', 'order_number', 'status', 'total_price', 'created_at']
    # No list_editable for status: the changelist form would bypass OrderAdminForm.clean_status
    # Map fields are excluded to avoid GDAL errors
    exclude = ['pickup_location', 'destination_location', 'route_geometry']

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        if hasattr(response, 'context_data') and 'cl' in response.context_data:
            response.context_data['summary_data'] = completed_orders_summary(response.context_data['cl'].queryset)
        return response

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change and 'status' in form.changed_data:
            # Status is already saved (validated by clean_status) - notify the client
            notify_order_update(obj.id, {'status': obj.status})
