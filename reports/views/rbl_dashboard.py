from django.shortcuts import render

def rbl_dashboard(request):
    return render(request, 'reports/placeholder_dashboard.html', {'area': 'RBL', 'HIDE_HEADER_FOOTER': not request.user.is_authenticated}) 