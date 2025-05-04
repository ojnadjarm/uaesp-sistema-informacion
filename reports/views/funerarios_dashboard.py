from django.shortcuts import render

def funerarios_dashboard(request):
    return render(request, 'reports/placeholder_dashboard.html', {'area': 'Funerarios', 'HIDE_HEADER_FOOTER': not request.user.is_authenticated}) 