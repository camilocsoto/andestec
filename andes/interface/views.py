from django.shortcuts import render
from dashboard.models import Variable
from django.core import serializers
# Create your views here.

def view_index(request):
    # Obtén los últimos 5 registros
    latest_variables = Variable.objects.order_by('-id')[:5]
    
    # Procesa los registros para separar la fecha y la hora
    processed_variables = []
    for variable in latest_variables:
        var_time_str = variable.var_time.strftime("%Y-%m-%d %H:%M:%S")
        date_part, time_part = var_time_str.split(" ")
        
        processed_variable = {
            'capacidad': variable.var_current_capacity,
            'temperatura': variable.var_temperature,
            'presion': variable.var_output_capacity,
            'bateria': variable.var_battery,
            'senial': variable.var_radiofrecuency,
            'fecha': date_part,
            'hora': time_part
        }
        processed_variables.append(processed_variable)

    context = {
        'segment': 'charts',
        'parent': 'apps',
        'variables': processed_variables
    }
    
    return render(request, 'dashboard/index.html', context)