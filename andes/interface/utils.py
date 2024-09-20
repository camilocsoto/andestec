from dashboard.models import Variable
import json

def get_latest_data():
    # get last five registers
    latest_variables = Variable.objects.order_by('-id')[:5]
    
    # Process the information of datetime that comes from the db.
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
            'grams': variable.var_grams,
            'hora': var_time_str,
            'minutes': time_part,
            'position': variable.localizacion
        }
        processed_variables.append(processed_variable)
        
    #get other information to send it to the template
    graph_data = collection_data(processed_variables) # main chart
    
    # at the end, clean this
    latest_variables = 0
    return {
        'objects':processed_variables,
        'charts':json.dumps(graph_data) 
        }
    
def collection_data(processed_variables):
    # process into lists the information required to to make the charts
    hours = []
    capacities = []
    outputs = []
    temperatures = []

    for variable in processed_variables:
        hours.append(variable['hora'])
        capacities.append(variable['capacidad'])
        outputs.append(variable['presion'])
        temperatures.append(variable['temperatura'])
    # oganize it as has to be
    hours.reverse()
    capacities.reverse()
    outputs.reverse()
    temperatures.reverse()
    graph_data = {
        'hour':hours,    
        'capacitiy':capacities,
        'output':outputs,
        'temp': temperatures,
    }
    return graph_data
    


