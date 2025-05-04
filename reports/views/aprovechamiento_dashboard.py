from django.shortcuts import render

def aprovechamiento_dashboard(request):
    return render(request, 'reports/placeholder_dashboard.html', {'area': 'Aprovechamiento', 'HIDE_HEADER_FOOTER': not request.user.is_authenticated}) 