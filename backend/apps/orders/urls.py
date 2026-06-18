from django.urls import path

from .views import (
    AvailableOrdersView,
    OrderCreateView,
    OrderActionView,
    OrderCancelByClientView,
    ActiveOrderByClientView,
    RouteInfoView,
    OrderDetailView
)

urlpatterns = [
    path("available/", AvailableOrdersView.as_view(), name="available-orders"),
    path("create/", OrderCreateView.as_view(), name="order-create"),
    path("route/", RouteInfoView.as_view(), name="order-route"),
    path("active/", ActiveOrderByClientView.as_view(), name="order-active"),
    path("<int:order_id>/action/", OrderActionView.as_view(), name="order-action"),
    path("<int:order_id>/cancel/", OrderCancelByClientView.as_view(), name="order-cancel"),
    path('<int:pk>/detail/', OrderDetailView.as_view()),
]