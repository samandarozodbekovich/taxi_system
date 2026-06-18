from django.urls import path

from .views_api import DriverLoginView, DriverRegisterView, DriverStatusView

from .views import driver_index, DriverLocationUpdateView

urlpatterns = [
    # api 
    path("register/", DriverRegisterView.as_view()),
    path("login/", DriverLoginView.as_view()),
    path("<int:pk>/status/", DriverStatusView.as_view()), 

    # web app
    path('panel/', driver_index),
    path("<int:pk>/location/", DriverLocationUpdateView.as_view()),
]
