from django.shortcuts import render
from .utils import compare_dates

def view_compare(request):
    #each minute, evaluate if can register the data.
    response_message = compare_dates()
    return render(request, 'variables_updated.html', {'status': response_message})
