from django.db import models
from ingesta.models.core.base import TimeStampedModel

class Servicio(TimeStampedModel):
    """
    Catálogo oficial de tipos de servicios.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único del servicio")
    nombre = models.CharField(max_length=100, help_text="Nombre oficial del servicio")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción adicional")
    categoria = models.CharField(max_length=100, blank=True, null=True, help_text="Categoría del servicio según tipo de procesamiento")
    activo = models.BooleanField(default=True, help_text="Indica si el servicio está activo")
    
    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
            models.Index(fields=['categoria']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
