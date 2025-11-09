from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from accounts.models import UserProfile
from accounts.utils import user_has_role
from globalfunctions.string_manager import get_string

def admin_required(view_func):
    """
    Decorador que verifica si el usuario es admin o superadmin.
    Si no tiene permisos, redirige con mensaje de error.
    """
    def check_admin(user):
        return user_has_role(user, {UserProfile.ROLE_ADMIN})
    
    decorated_view = user_passes_test(check_admin, login_url=None)(view_func)
    
    def wrapper(request, *args, **kwargs):
        if not check_admin(request.user):
            messages.error(request, get_string('errors.no_permissions', 'ingesta'))
            return redirect('coreview:dashboard')
        return decorated_view(request, *args, **kwargs)
    
    return wrapper

def admin_required_api(view_func):
    """
    Decorador para APIs que verifica si el usuario es admin o superadmin.
    Si no tiene permisos, retorna 403 Forbidden.
    """
    def check_admin(user):
        return user_has_role(user, {UserProfile.ROLE_ADMIN})
    
    def wrapper(request, *args, **kwargs):
        if not check_admin(request.user):
            return HttpResponseForbidden(get_string('errors.no_permissions', 'ingesta'))
        return view_func(request, *args, **kwargs)
    
    return wrapper
