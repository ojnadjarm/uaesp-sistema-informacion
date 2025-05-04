from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from globalfunctions.string_manager import get_string

def get_template_context():
    """
    Returns common template context variables.
    """
    return {
        'TEMPLATE_TITLE': get_string('templates.title', 'ingesta'),
        'TEMPLATE_NAVBAR_BRAND': get_string('templates.navbar_brand', 'ingesta'),
        'TEMPLATE_DASHBOARD': get_string('templates.dashboard', 'ingesta'),
        'TEMPLATE_UPLOAD_FILE': get_string('templates.upload_file', 'ingesta'),
        'TEMPLATE_FILE_HISTORY': get_string('templates.file_history', 'ingesta'),
        'TEMPLATE_REPORTS_TITLE': get_string('templates.reports_title', 'reports')
    }

def handle_error(request, error_message, template_name, context=None):
    """
    Handles errors consistently across views.
    """
    messages.error(request, error_message)
    if context is None:
        context = get_template_context()
    return render(request, template_name, context) 