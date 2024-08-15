from dashboard.models import Variable

def get_latest_data():
    # as compare_data makes the validation, if it's true, execute this function every minute.
    get_last_record = Variable.objects.latest('id')    
    #extract date and time
    var_time_str = get_last_record.var_time.strftime("%b. %d %Y, %I:%M %p")
    
    date_part, time_part = var_time_str.split(", ")[0:2]
    
    data = {
        'capacidad': get_last_record.var_capacity,
        'temperatura': get_last_record.var_temperature,
        'presion': get_last_record.var_presure,
        'bateria': get_last_record.var_battery,
        'senial': get_last_record.var_radiofrecuency,
        'hora': time_part,
        'dia': date_part
    }
    return data

