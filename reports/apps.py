from django.apps import AppConfig
from globalfunctions.string_manager import get_string

class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'
    verbose_name = 'Reportes e Indicadores'