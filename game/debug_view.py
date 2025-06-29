from django.http import JsonResponse
from django.shortcuts import render

def debug_view(request):
    """Simple debug view to test AJAX functionality."""
    if request.method == 'POST':
        return JsonResponse({
            'success': True,
            'message': 'AJAX is working!',
            'method': request.method,
            'data': dict(request.POST.items())
        })
    
    return render(request, 'game/debug.html')
