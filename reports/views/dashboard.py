from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from datetime import datetime, timedelta
from ingesta.models.disposicion.disposicion_final import DisposicionFinal
from ingesta.models.core.registro_carga import RegistroCarga
from coreview.base import get_template_context
from globalfunctions.string_manager import get_string

def reports_dashboard(request):
    context = {
        'HIDE_HEADER_FOOTER': not request.user.is_authenticated,
    }
    context.update(get_template_context())
    return render(request, 'reports/dashboard.html', context)