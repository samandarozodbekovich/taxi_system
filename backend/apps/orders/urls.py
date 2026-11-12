from django.urls import path

from .views import (
    AvailableOrdersView,
    OrderCreateView,
    OrderActionView,
    OrderCancelByClientView,
    ActiveOrderByClientView,
    RouteInfoView,
    OrderDetailView,
    OrderHistoryByClientView,
    DriverActiveOrderView,
    DriverOrderHistoryView,
)

urlpatterns = [
    path("available/", AvailableOrdersView.as_view(), name="available-orders"),
    path("driver/active/", DriverActiveOrderView.as_view(), name="driver-order-active"),
    path("driver/history/", DriverOrderHistoryView.as_view(), name="driver-order-history"),
    path("create/", OrderCreateView.as_view(), name="order-create"),
    path("route/", RouteInfoView.as_view(), name="order-route"),
    path("active/", ActiveOrderByClientView.as_view(), name="order-active"),
    path("history/", OrderHistoryByClientView.as_view(), name="order-history"),
    path("<int:order_id>/action/", OrderActionView.as_view(), name="order-action"),
    path("<int:order_id>/cancel/", OrderCancelByClientView.as_view(), name="order-cancel"),
    path('<int:pk>/detail/', OrderDetailView.as_view()),
]