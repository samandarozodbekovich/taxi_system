from django.urls import path
from .views import ClientCheckView

urlpatterns = [
    path('check/<int:tg_id>/', ClientCheckView.as_view(), name='client-check'),
    path('register/', ClientCheckView.as_view(), name='client-register'),
]