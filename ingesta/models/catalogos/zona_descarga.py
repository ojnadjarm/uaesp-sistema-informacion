from django.db import models
from ingesta.models.core.base import TimeStampedModel

class ZonaDescarga(TimeStampedModel):
    """
    Catálogo oficial de zonas de descarga.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único de la zona")
    nombre = models.CharField(max_length=100, help_text="Nombre oficial de la zona")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción adicional")
    activo = models.BooleanField(default=True, help_text="Indica si la zona está activa")
    
    class Meta:
        verbose_name = 'Zona de Descarga'
        verbose_name_plural = 'Zonas de Descarga'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
