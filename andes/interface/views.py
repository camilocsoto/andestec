from django.shortcuts import render
from .utils import get_latest_data

# Create your views here.

def view_index(request):
    context = get_latest_data()
    return render(request, 'dashboard/index.html', context)
