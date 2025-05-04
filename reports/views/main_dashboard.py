from django.shortcuts import render
from coreview.base import get_template_context
from globalfunctions.string_manager import get_string

def get_areas_misionales_context():
    """
    Retorna el contexto común de áreas misionales para todos los dashboards.
    """
    return {
        'AREAS_MISIONALES': [
            {
                'name': get_string('templates.disposicion_final', 'reports'),
                'url': 'reports:disposicion_final_dashboard',
                'icon': 'bi-trash',
                'color': 'primary',
            },
            {
                'name': get_string('templates.rbl', 'reports'),
                'url': 'reports:rbl_dashboard',
                'icon': 'bi-building-gear',
                'color': 'danger',
            },
            {
                'name': get_string('templates.aprovechamiento', 'reports'),
                'url': 'reports:aprovechamiento_dashboard',
                'icon': 'bi-recycle',
                'color': 'success',
            },
            {
                'name': get_string('templates.alumbrado', 'reports'),
                'url': 'reports:alumbrado_dashboard',
                'icon': 'bi-lightbulb',
                'color': 'warning',
            },
            {
                'name': get_string('templates.funerarios', 'reports'),
                'url': 'reports:funerarios_dashboard',
                'icon': 'bi-flower1',
                'color': 'info',
            },
        ]
    }

def main_dashboard(request):
    """
    Vista principal del módulo de reportes, muestra tarjetas para cada área misional.
    """
    context = {
        'TEMPLATE_DASHBOARD_TITLE': get_string('templates.reports_title', 'reports'),
        'TEMPLATE_DASHBOARD_DESCRIPTION': get_string('templates.reports_description', 'reports'),
        'HIDE_HEADER_FOOTER': not request.user.is_authenticated,
    }
    context.update(get_areas_misionales_context())
    context.update(get_template_context())
    return render(request, 'reports/main_dashboard.html', context)