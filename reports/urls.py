from django.urls import path
from .views import main_dashboard, disposicion_final_dashboard, rbl_dashboard, aprovechamiento_dashboard, alumbrado_dashboard, funerarios_dashboard
from .views import disposicion_final_reportes

app_name = 'reports'

urlpatterns = [
    path('', main_dashboard.main_dashboard, name='dashboard'),
    path('disposicion_final/', disposicion_final_dashboard.disposicion_final_dashboard, name='disposicion_final_dashboard'),
    path('disposicion_final_reportes/', disposicion_final_reportes.disposicion_final_reportes, name='disposicion_final_reportes'),
    path('disposicion_final_reportes/export/', disposicion_final_reportes.export_report_csv, name='df_export_report_csv'),
    path('rbl/', rbl_dashboard.rbl_dashboard, name='rbl_dashboard'),
    path('aprovechamiento/', aprovechamiento_dashboard.aprovechamiento_dashboard, name='aprovechamiento_dashboard'),
    path('alumbrado/', alumbrado_dashboard.alumbrado_dashboard, name='alumbrado_dashboard'),
    path('funerarios/', funerarios_dashboard.funerarios_dashboard, name='funerarios_dashboard'),
]