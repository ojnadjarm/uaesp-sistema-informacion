from django import template

from accounts.models import UserProfile
from accounts.utils import get_user_role, user_has_role

register = template.Library()


@register.filter
def has_role(user, role_name: str) -> bool:
    """
    Retorna True si el usuario tiene el rol indicado.
    """
    return user_has_role(user, {role_name})


@register.filter
def role_equals(user, role_name: str) -> bool:
    """
    Atajo para comparar el rol exacto del usuario.
    """
    return get_user_role(user) == role_name


@register.simple_tag
def role_constant(name: str) -> str:
    """
    Exponer los valores de las constantes de roles en templates.
    """
    return getattr(UserProfile, f"ROLE_{name.upper()}", name)

