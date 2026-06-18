from django.contrib import admin
from django import forms
from .models import Order

# Xaritani butunlay chetlab o'tish uchun widgetni o'zgartiramiz
class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        widgets = {
            'pickup_location': forms.TextInput(attrs={'readonly': 'readonly'}),
            'destination_location': forms.TextInput(attrs={'readonly': 'readonly'}),
            'route_geometry': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_number', 'status', 'total_price', 'created_at']
    list_editable = ['status']
    
    # MUHIM: GDAL xatosini butunlay o'ldirish uchun
    exclude = ['pickup_location', 'destination_location', 'route_geometry']

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            # Status o'zgarganda service orqali o'tkazamiz
            from apps.orders.services import OrderService
            # Modelni oddiy saqlaymiz
            super().save_model(request, obj, form, change)
            # Keyin WebSocket xabarini yuboramiz
            OrderService.update_status(obj.id, obj.status)
        else:
            super().save_model(request, obj, form, change)