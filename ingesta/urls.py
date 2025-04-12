from django.urls import path
from . import views

urlpatterns = [
    path('cargar/', views.upload_file_view, name='upload_file'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]