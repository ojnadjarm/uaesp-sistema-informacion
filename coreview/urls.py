from django.urls import path
from coreview.dashboard import dashboard_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
] 