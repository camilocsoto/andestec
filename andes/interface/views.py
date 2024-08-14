from django.shortcuts import render
from dashboard.models import Variable

# Create your views here.
def view_index(request):
    #send information to dashboard filter each device 🔥
    get_last_record = Variable.objects.latest('id')
    # instance each data:
    context = {
        'capacidad': get_last_record.var_capacity, #current % of capacity
        'temperatura': get_last_record.var_temperature,
        'presion': get_last_record.var_presure,
        'bateria': get_last_record.var_battery,
        'senial': get_last_record.var_radiofrecuency,
        'hora': get_last_record.var_time,
    }
    
    return render(request, 'dashboard/index.html', context)