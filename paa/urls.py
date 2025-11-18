from django.urls import path
from . import views

app_name = 'paa'

urlpatterns = [
    path('', views.paa_list, name='list'),
    path('mis-solicitudes/', views.mis_solicitudes, name='my_requests'),
    path('mis-solicitudes/<int:pk>/editar/', views.solicitud_edit, name='solicitud_edit'),
    path('mis-solicitudes/<int:pk>/eliminar/', views.solicitud_delete, name='solicitud_delete'),
    path('crear/', views.paa_create, name='create'),
    path('<int:pk>/editar/', views.paa_edit, name='edit'),
    path('<int:pk>/eliminar/', views.paa_delete, name='delete'),
    path('aprobaciones/', views.paa_approval_list, name='approval_list'),
    path('aprobaciones/<int:pk>/', views.paa_approval_detail, name='approval_detail'),
]

