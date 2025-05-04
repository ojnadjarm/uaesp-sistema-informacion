from django.shortcuts import render

def alumbrado_dashboard(request):
    return render(request, 'reports/placeholder_dashboard.html', {'area': 'Alumbrado', 'HIDE_HEADER_FOOTER': not request.user.is_authenticated}) 