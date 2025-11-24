from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from globalfunctions.string_manager import get_string
import time

# Versión para invalidar caché de activos estáticos (cambia al reiniciar el servidor)
STATIC_VERSION = str(int(time.time()))

def get_template_context():
    """
    Retorna variables de contexto comunes para las plantillas.
    """
    return {
        'TEMPLATE_TITLE': get_string('templates.title', 'ingesta'),
        'TEMPLATE_NAVBAR_BRAND': get_string('templates.navbar_brand', 'ingesta'),
        'TEMPLATE_DASHBOARD': get_string('templates.dashboard', 'ingesta'),
        'TEMPLATE_UPLOAD_FILE': get_string('templates.upload_file', 'ingesta'),
        'TEMPLATE_FILE_HISTORY': get_string('templates.file_history', 'ingesta'),
        'TEMPLATE_REPORTS_TITLE': get_string('templates.reports_title', 'reports'),
        'TEMPLATE_LOGOUT': get_string('templates.logout', 'ingesta'),
        'TEMPLATE_GREETING': get_string('templates.greeting', 'ingesta'),
        'TEMPLATE_REPORT_DISPOSICION_FINAL': get_string('templates.disposicion_final', 'reports'),
        'TEMPLATE_REPORT_APROVECHAMIENTO': get_string('templates.aprovechamiento', 'reports'),
        'TEMPLATE_REPORT_ALUMBRADO': get_string('templates.alumbrado', 'reports'),
        'TEMPLATE_REPORT_FUNERARIOS': get_string('templates.funerarios', 'reports'),
        'TEMPLATE_REPORT_RBL': get_string('templates.rbl', 'reports'),
        'TEMPLATE_CATALOGOS_TITLE': get_string('catalogos.title', 'ingesta'),
        'TEMPLATE_CATALOGOS_DESCRIPTION': get_string('catalogos.description', 'ingesta'),
        'TEMPLATE_CATALOGOS_CONCESION': get_string('catalogos.concesion.title', 'ingesta'),
        'TEMPLATE_CATALOGOS_ASE': get_string('catalogos.ase.title', 'ingesta'),
        'TEMPLATE_CATALOGOS_SERVICIO': get_string('catalogos.servicio.title', 'ingesta'),
        'TEMPLATE_CATALOGOS_ZONA_DESCARGA': get_string('catalogos.zona_descarga.title', 'ingesta'),
        'TEMPLATE_PAA_MENU_TITLE': get_string('menu.title', 'paa'),
        'TEMPLATE_PAA_MENU_LIST': get_string('menu.list', 'paa'),
        'TEMPLATE_PAA_MENU_CREATE': get_string('menu.create', 'paa'),
        'TEMPLATE_PAA_MENU_APPROVALS': get_string('menu.approvals', 'paa'),
        'TEMPLATE_PAA_MENU_MY_REQUESTS': get_string('menu.my_requests', 'paa'),
        'STATIC_VERSION': STATIC_VERSION,
    }

def handle_error(request, error_message, template_name, context=None):
    """
    Maneja los errores de manera consistente a través de las vistas.
    """
    messages.error(request, error_message)
    if context is None:
        context = get_template_context()
    return render(request, template_name, context)