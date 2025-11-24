from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class UserProfile(models.Model):
    ROLE_ADMIN = "admin"
    ROLE_DATA_INGESTOR = "data_ingestor"
    ROLE_REGISTER_USER = "register_user"
    ROLE_EDITOR_PAA = "editor_paa"
    ROLE_MASTER_PAA = "master_paa"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_DATA_INGESTOR, "Data Ingestor"),
        (ROLE_REGISTER_USER, "Register User"),
        (ROLE_EDITOR_PAA, "Editor PAA"),
        (ROLE_MASTER_PAA, "Master PAA"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=32,
        choices=ROLE_CHOICES,
        default=ROLE_REGISTER_USER,
    )
    teams = ArrayField(
        base_field=models.CharField(max_length=100),
        blank=True,
        default=list,
        help_text=(
            "Identificadores de subsecretaría/proceso permitidos para carga de datos. "
            "Dejar vacío para permitir todos (solo administradores)."
        ),
    )

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

    def __str__(self):
        return f"{self.user.username} ({self.role})"

