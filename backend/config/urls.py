
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from apps.drivers.views import protected_media

urlpatterns = [
    path('', TemplateView.as_view(template_name="webapp/index.html"), name='home'),
    
    path("api/admin/", admin.site.urls),
    path("api/orders/", include("apps.orders.urls")),
    path("api/clients/", include("apps.clients.urls")),
    path("api/drivers/", include("apps.drivers.urls")),
    path("api/wallet/", include("apps.wallet.urls")),
    # Driver photos: admin staff only (MEDIA_URL)
    path("media/<path:path>", protected_media),
]
