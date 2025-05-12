from django.db import models
from ingesta.models.core.base import TimeStampedModel

class DisposicionFinalMensual(TimeStampedModel):
    """
    Modelo para almacenar datos mensuales agregados de disposiciones finales.
    Optimizado para consultas mensuales frecuentes.
    """
    year = models.IntegerField()
    month = models.IntegerField()
    concesion = models.CharField(max_length=60, null=True, blank=True)
    ase = models.CharField(max_length=60, null=True, blank=True)
    servicio = models.CharField(max_length=60, null=True, blank=True)
    zona_descarga = models.CharField(max_length=60, null=True, blank=True)
    peso_residuos = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    tipo_proceso = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        verbose_name = 'Disposición Final Mensual'
        verbose_name_plural = 'Disposiciones Finales Mensuales'
        ordering = ['-year', '-month']
        indexes = [
            models.Index(fields=['year', 'month']),
            models.Index(fields=['concesion']),
            models.Index(fields=['ase']),
        ]
        unique_together = ['year', 'month', 'concesion', 'ase', 'servicio', 'zona_descarga', 'tipo_proceso']

    def __str__(self):
        return f"{self.year}-{self.month:02d} - {self.concesion or 'Sin concesión'} - {self.ase or 'Sin ASE'}" 