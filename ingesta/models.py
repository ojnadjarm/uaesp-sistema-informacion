from django.db import models
import uuid

class RegistroCarga(models.Model):
    ESTADOS = (
        ('RECIBIDO', 'Recibido en Django'),
        ('EN_MINIO', 'Subido a MinIO'),
        ('PROCESANDO_NIFI', 'Procesando por NiFi'),
        ('ERROR', 'Error'),
        ('COMPLETADO', 'Completado'),
    )
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_archivo_original = models.CharField(max_length=255)
    path_minio = models.CharField(max_length=500, blank=True, null=True)
    fecha_hora_carga = models.DateTimeField(auto_now_add=True)
    subsecretaria_origen = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='RECIBIDO')
    mensaje_error = models.TextField(blank=True, null=True)
    tipo_proceso = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_archivo_original} ({self.fecha_hora_carga.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        ordering = ['-fecha_hora_carga']