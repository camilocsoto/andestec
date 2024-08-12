from django.shortcuts import get_object_or_404
from .models import Sensor, Variable
from api.utils import process_sensor_data
"""
this should execute when the sensor is previous registered:
process to keep information of the sensor.
"""
def get_data_sensor():
    #connect with utils (api) to bring the organized data.
    data_from_api = process_sensor_data()
    return data_from_api

def search_last_item():
    try:
        # connect with the db to bring the last record in variables table
        last_object = Variable.objects.latest('id')
        threted_date = str(last_object.var_time).split('+')[0]
        return threted_date
    except Variable.DoesNotExist:
        # case: the sensors doesn't any keep data in the db 
        # always commit the first record.
        return 0
    
def compare_dates():
    # add first register to variables table
    is_variable = search_last_item()
    if is_variable == 0:
        return keep_variables()
    
    # if exists data in variables table:
    sensor_date = get_data_sensor()
    if sensor_date['heartbeatDate'] == is_variable:
        # won't keep the same register in the db
        return "cannot add, please wait"
    else:
        return keep_variables()

    
def keep_variables():
    # make every operation to upload the data at variables table.
    try:
        data_from_api = get_data_sensor()
        # link the sensor where the variable belongs
        sensor = get_object_or_404(Sensor, sen_serialno = data_from_api['deviceNo'])
        # extract info of the specific sensor:
        _id = int(sensor.sen_id)
        sen_max_capacity = sensor.max_capacity
        """
        steps to find the current % of gas in the bowl
        1° you gotta find the relative preassure: Prel = Pmed + Patm
        Where:
        Prel = real pressure of the bowl in psi
        Pmed = data_from_api['pressure'] in psi
        Patm = 14,7 psi
        2° rule of 3 => get the % of gas: (Prel/sen_max_capacity)*100
        """
        Prel = float(data_from_api['pressure']) + 14,7
        current_capacity = (Prel[0]/float(sen_max_capacity))*100
        # 🟠 processing information and keep it
        # create instance to foreign key
        sensor_instance = get_object_or_404(Sensor, sen_id=_id)
        # Upload the database: 
        Variable.objects.create(
            var_temperature = data_from_api['temperature'],
            var_radiofrecuency = data_from_api['signal'],
            var_presure = Prel[0],
            var_time = data_from_api['heartbeatDate'], 
            var_capacity = current_capacity, #most important than anything
            var_battery =data_from_api['battery'],
            sensors_sen_id = sensor_instance, #use the instance here
            localizacion = "not available yet!",
        )
        return "the data has been kept succesfully"
    except Exception as e:
        return f"error finded: {e}"
    
    # keep the threated information.
     
    
    