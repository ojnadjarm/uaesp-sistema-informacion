from django.urls import path
from .views import main_dashboard, disposicion_final_dashboard, rbl_dashboard, aprovechamiento_dashboard, alumbrado_dashboard, funerarios_dashboard

app_name = 'reports'

urlpatterns = [
    path('', main_dashboard.main_dashboard, name='dashboard'),
    path('disposicion_final/', disposicion_final_dashboard.disposicion_final_dashboard, name='disposicion_final_dashboard'),
    path('rbl/', rbl_dashboard.rbl_dashboard, name='rbl_dashboard'),
    path('aprovechamiento/', aprovechamiento_dashboard.aprovechamiento_dashboard, name='aprovechamiento_dashboard'),
    path('alumbrado/', alumbrado_dashboard.alumbrado_dashboard, name='alumbrado_dashboard'),
    path('funerarios/', funerarios_dashboard.funerarios_dashboard, name='funerarios_dashboard'),
    # Puedes agregar aquí las rutas para rbl, aprovechamiento, alumbrado, funerarios
] 