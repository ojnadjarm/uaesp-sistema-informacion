from django.shortcuts import render
from coreview.base import get_template_context
from globalfunctions.string_manager import get_string
from .main_dashboard import get_areas_misionales_context


def rbl_dashboard(request):
    area_name = get_string('templates.rbl', 'reports')
    context = {
        'area': area_name,
        'TEMPLATE_PLACEHOLDER_HEADING': get_string('templates.placeholder_dashboard_heading', 'reports').format(area=area_name),
        'HIDE_HEADER_FOOTER': not request.user.is_authenticated,
    }
    context.update(get_areas_misionales_context())
    context.update(get_template_context())
    return render(request, 'reports/placeholder_dashboard.html', context)