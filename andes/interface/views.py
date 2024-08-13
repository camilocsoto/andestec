from django.shortcuts import render

# Create your views here.
def view_index(request):
    return render(request, 'dashboard/index.html')
"""
def signin_view(request):
    # lógica de la vista de inicio de sesión
    return render(request, 'signin.html')
    """