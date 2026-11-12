from django import forms

from apps.wallet.models import WalletTransaction
from apps.wallet.functions.apply_wallet_transaction import BALANCE_SIGN


class WalletTransactionAdminForm(forms.ModelForm):
    """Admin can add only manual transactions; commissions are created by the system."""

    class Meta:
        model = WalletTransaction
        fields = ['wallet', 'transaction_type', 'amount', 'note']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'transaction_type' in self.fields:
            self.fields['transaction_type'].choices = [
                choice for choice in WalletTransaction.TRANSACTION_TYPES if choice[0] in BALANCE_SIGN
            ]

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("The amount must be positive.")
        return amount
