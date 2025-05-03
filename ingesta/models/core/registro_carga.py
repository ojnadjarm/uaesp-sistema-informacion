from django.db import models
from .base import TimeStampedModel, EstadoModel
from datetime import datetime

class RegistroCargaManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def completados(self):
        return self.get_queryset().filter(estado='COMPLETADO')

    def en_proceso(self):
        return self.get_queryset().filter(estado__in=['EN_MINIO', 'PROCESANDO_NIFI'])

    def con_errores(self):
        return self.get_queryset().filter(estado='ERROR')

class RegistroCarga(TimeStampedModel, EstadoModel):
    """
    Modelo para registrar las cargas de archivos en el sistema.
    """
    nombre_archivo_original = models.CharField(max_length=255)
    path_minio = models.CharField(max_length=500, blank=True, null=True)
    fecha_hora_carga = models.DateTimeField(auto_now_add=True)
    subsecretaria_origen = models.CharField(max_length=100, blank=True, null=True)
    tipo_proceso = models.CharField(max_length=50, blank=True, null=True)

    objects = RegistroCargaManager()

    def __str__(self):
        return f"{self.nombre_archivo_original} ({self.fecha_hora_carga.strftime('%Y-%m-%d %H:%M')})"

    def marcar_como_completado(self):
        """Marca el registro como completado."""
        self.estado = 'COMPLETADO'
        self.save()

    def marcar_como_error(self, mensaje):
        """Marca el registro como error con un mensaje específico."""
        self.estado = 'ERROR'
        self.mensaje_error = mensaje
        self.save()

    class Meta:
        ordering = ['-fecha_hora_carga']
        verbose_name = 'Registro de Carga'
        verbose_name_plural = 'Registros de Carga'
        indexes = [
            models.Index(fields=['fecha_hora_carga']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo_proceso']),
        ] 