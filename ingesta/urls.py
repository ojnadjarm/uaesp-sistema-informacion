from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('historial/', views.file_history_view, name='file_history'),
    path('cargar/', views.upload_file_view, name='upload_file'),
    path('download_file/<int:file_id>/', views.download_file, name='download_file'),
    path('delete_file/<int:file_id>/', views.delete_file, name='delete_file'),
]