from django.urls import path

from .views import InfoWalletView

urlpatterns = [
    path(
        "info/",
        InfoWalletView.as_view(),
        name="wallet-info"
    ),
]