from django.db import models
from django.contrib.auth import get_user_model
from ingesta.models.core.registro_carga import RegistroCarga
from ingesta.models.disposicion.disposicion_final import DisposicionFinal
from globalfunctions.string_manager import get_string

User = get_user_model()

class ReportConfig(models.Model):
    """
    Configuración de reportes personalizados por usuario.
    """
    name = models.CharField(max_length=100, verbose_name=get_string("models.report_name", "reports"))
    description = models.TextField(blank=True, null=True, verbose_name=get_string("models.report_description", "reports"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=get_string("models.user", "reports"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Configuración de filtros
    start_date = models.DateField(verbose_name=get_string("models.start_date", "reports"))
    end_date = models.DateField(verbose_name=get_string("models.end_date", "reports"))
    subsecretaria = models.CharField(max_length=100, blank=True, null=True, verbose_name=get_string("models.subsecretaria", "reports"))
    tipo_proceso = models.CharField(max_length=50, blank=True, null=True, verbose_name=get_string("models.tipo_proceso", "reports"))

    # Configuración de visualización
    chart_type = models.CharField(
        max_length=20,
        choices=[
            ('line', get_string("models.chart_line", "reports")),
            ('bar', get_string("models.chart_bar", "reports")),
            ('pie', get_string("models.chart_pie", "reports")),
            ('table', get_string("models.chart_table", "reports")),
        ],
        default='table',
        verbose_name=get_string("models.chart_type", "reports")
    )
    
    class Meta:
        verbose_name = get_string('models.report_config', 'reports')
        verbose_name_plural = get_string('models.report_configs', 'reports')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} - {self.user.username}"

class Indicator(models.Model):
    """
    Modelo para definir indicadores calculados.
    """
    name = models.CharField(max_length=100, verbose_name=get_string("models.indicator_name", "reports"))
    description = models.TextField(verbose_name=get_string("models.indicator_description", "reports"))
    formula = models.TextField(verbose_name=get_string("models.indicator_formula", "reports"))
    unit = models.CharField(max_length=20, verbose_name=get_string("models.indicator_unit", "reports"))
    category = models.CharField(
        max_length=50,
        choices=[
            ('disposicion', get_string("models.category_disposicion", "reports")),
            ('pesaje', get_string("models.category_pesaje", "reports")),
            ('general', get_string("models.category_general", "reports")),
        ],
        verbose_name=get_string("models.indicator_category", "reports")
    )
    
    class Meta:
        verbose_name = get_string('models.indicator', 'reports')
        verbose_name_plural = get_string('models.indicators', 'reports')
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category})" 