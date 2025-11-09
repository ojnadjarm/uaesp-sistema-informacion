from functools import wraps
from typing import Iterable, Optional, Set

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import UserProfile


def get_user_profile(user) -> Optional[UserProfile]:
    if not hasattr(user, "profile"):
        return None
    try:
        return user.profile
    except UserProfile.DoesNotExist:
        return None


def get_user_role(user) -> Optional[str]:
    if not getattr(user, "is_authenticated", False):
        return None
    if getattr(user, "is_superuser", False):
        return UserProfile.ROLE_ADMIN
    profile = get_user_profile(user)
    if profile:
        return profile.role
    return UserProfile.ROLE_REGISTER_USER


def user_has_role(user, roles: Iterable[str]) -> bool:
    """
    Retorna True si el usuario tiene alguno de los roles especificados.
    """
    role = get_user_role(user)
    if role == UserProfile.ROLE_ADMIN:
        return True
    return role in set(roles)


def user_allowed_subsecretarias(user) -> Optional[Set[str]]:
    """
    Devuelve el conjunto de subsecretarías permitidas para el usuario.
    None significa acceso completo (admins).
    """
    role = get_user_role(user)
    if role == UserProfile.ROLE_ADMIN:
        return None
    profile = get_user_profile(user)
    if profile and profile.teams:
        return set(profile.teams)
    return set()


def role_required(allowed_roles: Iterable[str], allow_admin: bool = True):
    """
    Decorador que garantiza que el usuario tenga alguno de los roles permitidos.
    Los administradores siempre son permitidos por defecto.
    """

    allowed_roles = set(allowed_roles)

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if allow_admin and user_has_role(request.user, {UserProfile.ROLE_ADMIN}):
                return view_func(request, *args, **kwargs)
            if user_has_role(request.user, allowed_roles):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied

        return _wrapped_view

    return decorator


def user_can_access_reports(user) -> bool:
    """
    Todos los usuarios (incluyendo anónimos) pueden acceder a los reportes básicos.
    """
    return True


def user_can_access_custom_reports(user) -> bool:
    """
    Solo administradores y usuarios con rol register_user pueden acceder
    al constructor de reportes personalizados.
    """
    if not getattr(user, "is_authenticated", False):
        return False
    return user_has_role(user, {UserProfile.ROLE_REGISTER_USER})


def user_can_upload_files(user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    return user_has_role(user, {UserProfile.ROLE_DATA_INGESTOR})


def user_can_view_ingesta_history(user) -> bool:
    """
    Puede ver historial de cargas/evidencias si puede subir archivos.
    """
    return user_can_upload_files(user)


def user_can_manage_catalogs(user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    return user_has_role(user, {UserProfile.ROLE_ADMIN})


def filter_queryset_by_subsecretarias(queryset, user, field_name: str):
    """
    Filtra un queryset por las subsecretarías permitidas del usuario.
    """
    allowed = user_allowed_subsecretarias(user)
    if allowed is None:
        return queryset
    if not allowed:
        return queryset.none()
    return queryset.filter(**{f"{field_name}__in": allowed})


def is_subsecretaria_allowed(user, subsecretaria: Optional[str]) -> bool:
    allowed = user_allowed_subsecretarias(user)
    if allowed is None:
        return True
    if not subsecretaria:
        return False
    return subsecretaria in allowed

