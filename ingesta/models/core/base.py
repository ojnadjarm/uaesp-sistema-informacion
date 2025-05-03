from django.db import models
from datetime import datetime

def get_current_timestamp():
    return int(datetime.now().timestamp())

class TimeStampedModel(models.Model):
    """
    Abstract base model that provides timestamp fields.
    """
    fecha_creacion = models.BigIntegerField(default=get_current_timestamp)
    fecha_actualizacion = models.BigIntegerField(default=get_current_timestamp)

    def save(self, *args, **kwargs):
        self.fecha_actualizacion = int(datetime.now().timestamp())
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class EstadoModel(models.Model):
    """
    Abstract base model that provides state management.
    """
    ESTADOS = (
        ('RECIBIDO', 'Recibido en Django'),
        ('EN_MINIO', 'Subido a MinIO'),
        ('PROCESANDO_NIFI', 'Procesando por NiFi'),
        ('ERROR', 'Error'),
        ('COMPLETADO', 'Completado'),
    )
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='RECIBIDO')
    mensaje_error = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True 