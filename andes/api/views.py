from django.shortcuts import render
from .utils import process_sensor_data    

def view_sensor_data(request): # si pones *args **kwgars, el id se guarda ahí...
    # Instance of the json received from the api (clase 13 platzi)
    processed_data = process_sensor_data() # si se le pide el parametro, solo te va a actualizar los que necesitas
    return render(request, 'api/load_data.html', {'processed_data': processed_data})
