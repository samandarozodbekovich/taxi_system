from django import forms

from apps.orders.models import Order

# Statuses an operator may set by hand. The others are side effects of what the driver or the
# system does (accepting assigns a driver, starting sets timestamps) and are left to them.
ADMIN_SETTABLE_STATUSES = ('CANCELED', 'COMPLETED')


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        # Read-only text inputs instead of map widgets
        widgets = {
            'pickup_location': forms.TextInput(attrs={'readonly': 'readonly'}),
            'destination_location': forms.TextInput(attrs={'readonly': 'readonly'}),
            'route_geometry': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def clean_status(self):
        # The admin is also bound by the status machine (e.g. COMPLETED -> SEARCHING is not allowed)
        new_status = self.cleaned_data['status']
        if self.instance.pk:
            current = Order.objects.only('status', 'driver_id').get(pk=self.instance.pk)
            if new_status == current.status:
                return new_status
            if new_status not in ADMIN_SETTABLE_STATUSES:
                raise forms.ValidationError(
                    f"Only {', '.join(ADMIN_SETTABLE_STATUSES)} can be set here; the other statuses are set by the driver."
                )
            if not current.can_transition_to(new_status):
                allowed = ", ".join(sorted(Order.ALLOWED_TRANSITIONS.get(current.status, ()))) or "none"
                raise forms.ValidationError(f"Cannot change {current.status} to {new_status}. Allowed: {allowed}.")
        return new_status
