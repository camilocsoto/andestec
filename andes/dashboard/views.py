from django.shortcuts import render
from .utils import compare_dates, keep_variables
"""
still we've gotta see how to execute it in second plane.
"""
def view_compare(request):
    #each minute, evaluate if can register the data.
    # 🧟‍♀️ response_message = compare_dates()
    response_message = keep_variables()
    return render(request, 'dashboard/variables_updated.html', {'status': response_message})
