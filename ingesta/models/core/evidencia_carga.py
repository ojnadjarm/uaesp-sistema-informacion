from django.db import models
from django.contrib.auth import get_user_model
from .base import TimeStampedModel
from .registro_carga import RegistroCarga

User = get_user_model()


class EvidenciaCarga(TimeStampedModel):
    """
    Evidencia (documento de respaldo) asociada a un RegistroCarga.
    Archivos se almacenan en MinIO y aquí se guarda la referencia.
    """
    registro_carga = models.ForeignKey(
        RegistroCarga,
        related_name='evidencias',
        on_delete=models.CASCADE
    )
    nombre_archivo_original = models.CharField(max_length=255)
    path_minio = models.CharField(max_length=500)
    fecha_hora_subida = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)
    size_bytes = models.BigIntegerField(blank=True, null=True)
    content_type = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"Evidencia: {self.nombre_archivo_original} ({self.registro_carga_id})"

    class Meta:
        verbose_name = 'Evidencia de Carga'
        verbose_name_plural = 'Evidencias de Carga'
        indexes = [
            models.Index(fields=['registro_carga']),
            models.Index(fields=['fecha_hora_subida']),
        ]


