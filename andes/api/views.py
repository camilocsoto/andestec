from django.shortcuts import render
from .utils import process_sensor_data    

def view_sensor_data(request):
    # Instance of the json received from the api
    processed_data = process_sensor_data()
    return render(request, 'api/load_data.html', {'processed_data': processed_data})
