from django.shortcuts import render
from coreview.base import get_template_context
from .main_dashboard import get_areas_misionales_context

def alumbrado_dashboard(request):
    context = {
        'area': 'Alumbrado',
        'HIDE_HEADER_FOOTER': not request.user.is_authenticated,
    }
    context.update(get_areas_misionales_context())
    context.update(get_template_context())
    return render(request, 'reports/placeholder_dashboard.html', context) 