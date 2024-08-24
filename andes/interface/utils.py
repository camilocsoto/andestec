from dashboard.models import Variable
import json

def get_latest_data():
    # get last five registers
    latest_variables = Variable.objects.order_by('-id')[:5]
    
    # Procesa los registros para separar la fecha y la hora
    processed_variables = []
    for variable in latest_variables:
        var_time_str = variable.var_time.strftime("%Y-%m-%d  %H:%M %p")
        date_part, time_part = var_time_str.split("  ")
        
        processed_variable = {
            'capacidad': variable.var_current_capacity,
            'temperatura': float(variable.var_temperature),
            'presion': variable.var_output_capacity,
            'bateria': variable.var_battery,
            'senial': variable.var_radiofrecuency,
            'fecha': date_part,
            'hora': time_part
        }
        processed_variables.append(processed_variable)

    # process the information required to to make the charts
    hours = []
    capacities = []
    outputs = []

    for variable in processed_variables:
        hours.append(variable['hora'])
        capacities.append(variable['capacidad'])
        outputs.append(variable['presion'])
    # oganize it as has to be
    hours.reverse()
    capacities.reverse()
    outputs.reverse()
    graph_data = {
        'hour':hours,    
        'capacitiy':capacities,
        'output':outputs
    }
    # at the end, clean this
    latest_variables = 0
    
    #serialize the info to render the html faster    
    return {
            'objects':processed_variables,
            'charts':json.dumps(graph_data) 
        }


