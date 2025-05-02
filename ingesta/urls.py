from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('historial/', views.file_history_view, name='file_history'),
    path('cargar/', views.upload_file_view, name='upload_file'),
]