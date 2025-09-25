from django.db import models
from ingesta.models.core.base import TimeStampedModel

class Concesion(TimeStampedModel):
    """
    Catálogo oficial de concesiones de servicios públicos.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único de la concesión")
    nombre = models.CharField(max_length=100, help_text="Nombre oficial de la concesión")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción adicional")
    categoria = models.CharField(max_length=100, blank=True, null=True, help_text="Categoría de la concesión según origen del residuo")
    activo = models.BooleanField(default=True, help_text="Indica si la concesión está activa")
    
    class Meta:
        verbose_name = 'Concesión'
        verbose_name_plural = 'Concesiones'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
            models.Index(fields=['categoria']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
