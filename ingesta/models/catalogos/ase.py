from django.db import models
from ingesta.models.core.base import TimeStampedModel

class ASE(TimeStampedModel):
    """
    Catálogo oficial de ASEs (Empresas de Servicios Públicos).
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único del ASE")
    nombre = models.CharField(max_length=100, help_text="Nombre oficial del ASE")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción adicional")
    activo = models.BooleanField(default=True, help_text="Indica si el ASE está activo")
    
    class Meta:
        verbose_name = 'ASE'
        verbose_name_plural = 'ASEs'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
