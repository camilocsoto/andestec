from django.shortcuts import render, get_object_or_404
from api.utils import process_sensor_data
from .models import Sensor, Variable
# Create your views here.

def keep_data_of_sensors(request):
    # make every operation to upload the data at variables table.
    #below, "sensor" keep the item in the database to get few values
    data_from_api = process_sensor_data()
    sensor = get_object_or_404(Sensor, serial_number = data_from_api['deviceNo'])
    # get few values to create the object variables.
    sen_id = sensor.id
    sen_max_capacity = sensor.max_capacity
    
    """
    steps to find the current % of gas in the bowl
    1° you gotta find the relative preassure like: Prel = Pmed + Patm
    Where:
    Prel = real pressure of the bowl in psi
    Pmed = data_from_api['pressure'] in psi
    Patm = 14,7 psi
    2° rule of 3 => get the % of gas: (Prel/sen_max_capacity)*100
    """
    Prel = int(data_from_api['pressure']) + 14,7
    current_capacity = (Prel/int(sen_max_capacity))*100
    
    # Upload the database: still I've gotta repair it for missing datetime
    Variable.objects.create(
        var_temperature = data_from_api['temperature'],
        var_radiofrecuency = data_from_api['signal'],
        var_presure = Prel,
        dateTime = data_from_api['heartbeatDate'], 
        var_capacity = current_capacity, #most important than anything
        var_battery =data_from_api['battery'],
        sensors_sen_id =sen_id,
        localizacion = "not available yet!",
    )
    