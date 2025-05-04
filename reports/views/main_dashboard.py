from django.shortcuts import render
from coreview.base import get_template_context
from globalfunctions.string_manager import get_string

def main_dashboard(request):
    """
    Vista principal del módulo de reportes, muestra tarjetas para cada área misional.
    """
    context = {
        'TEMPLATE_DASHBOARD_TITLE': get_string('templates.reports_title', 'reports'),
        'TEMPLATE_DASHBOARD_DESCRIPTION': get_string('templates.reports_description', 'reports'),
        'HIDE_HEADER_FOOTER': not request.user.is_authenticated,
        'AREAS_MISIONALES': [
            {
                'name': get_string('templates.disposicion_final', 'reports'),
                'url': 'reports:disposicion_final_dashboard',
                'icon': 'bi-recycle',
            },
            {
                'name': get_string('templates.rbl', 'reports'),
                'url': 'reports:rbl_dashboard',
                'icon': 'bi-truck',
            },
            {
                'name': get_string('templates.aprovechamiento', 'reports'),
                'url': 'reports:aprovechamiento_dashboard',
                'icon': 'bi-arrow-repeat',
            },
            {
                'name': get_string('templates.alumbrado', 'reports'),
                'url': 'reports:alumbrado_dashboard',
                'icon': 'bi-lightbulb',
            },
            {
                'name': get_string('templates.funerarios', 'reports'),
                'url': 'reports:funerarios_dashboard',
                'icon': 'bi-people',
            },
        ]
    }
    context.update(get_template_context())
    return render(request, 'reports/main_dashboard.html', context)