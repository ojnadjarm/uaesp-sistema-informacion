from django.urls import path
from . import views
from .views import catalogos

app_name = 'ingesta'

urlpatterns = [
    path('historial/', views.file_history_view, name='file_history'),
    path('cargar/', views.upload_file_view, name='upload_file'),
    path('download_file/<int:file_id>/', views.download_file, name='download_file'),
    path('download_error_file/', views.download_error_file, name='download_error_file'),
    path('delete_file/<int:file_id>/', views.delete_file, name='delete_file'),
    
    # URLs para catálogos
    # Concesiones
    path('catalogos/concesiones/', catalogos.concesion_list, name='concesion_list'),
    path('catalogos/concesiones/crear/', catalogos.concesion_create, name='concesion_create'),
    path('catalogos/concesiones/<int:pk>/editar/', catalogos.concesion_edit, name='concesion_edit'),
    path('catalogos/concesiones/<int:pk>/eliminar/', catalogos.concesion_delete, name='concesion_delete'),
    path('catalogos/concesiones/<int:pk>/toggle/', catalogos.concesion_toggle, name='concesion_toggle'),
    
    # ASEs
    path('catalogos/ases/', catalogos.ase_list, name='ase_list'),
    path('catalogos/ases/crear/', catalogos.ase_create, name='ase_create'),
    path('catalogos/ases/<int:pk>/editar/', catalogos.ase_edit, name='ase_edit'),
    path('catalogos/ases/<int:pk>/eliminar/', catalogos.ase_delete, name='ase_delete'),
    path('catalogos/ases/<int:pk>/toggle/', catalogos.ase_toggle, name='ase_toggle'),
    
    # Servicios
    path('catalogos/servicios/', catalogos.servicio_list, name='servicio_list'),
    path('catalogos/servicios/crear/', catalogos.servicio_create, name='servicio_create'),
    path('catalogos/servicios/<int:pk>/editar/', catalogos.servicio_edit, name='servicio_edit'),
    path('catalogos/servicios/<int:pk>/eliminar/', catalogos.servicio_delete, name='servicio_delete'),
    path('catalogos/servicios/<int:pk>/toggle/', catalogos.servicio_toggle, name='servicio_toggle'),
    
    # Zonas de descarga
    path('catalogos/zonas-descarga/', catalogos.zona_descarga_list, name='zona_descarga_list'),
    path('catalogos/zonas-descarga/crear/', catalogos.zona_descarga_create, name='zona_descarga_create'),
    path('catalogos/zonas-descarga/<int:pk>/editar/', catalogos.zona_descarga_edit, name='zona_descarga_edit'),
    path('catalogos/zonas-descarga/<int:pk>/eliminar/', catalogos.zona_descarga_delete, name='zona_descarga_delete'),
    path('catalogos/zonas-descarga/<int:pk>/toggle/', catalogos.zona_descarga_toggle, name='zona_descarga_toggle'),
]
