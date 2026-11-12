from django.urls import path
from .views import ClientBonusView, ClientCheckView

urlpatterns = [
    path('check/<int:tg_id>/', ClientCheckView.as_view(), name='client-check'),
    path('register/', ClientCheckView.as_view(), name='client-register'),
    path('bonus/', ClientBonusView.as_view(), name='client-bonus'),
]