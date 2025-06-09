from django.views.generic.base import TemplateView
from .utils import get_latest_data
from django.shortcuts import render
from .sensors import process_sensor_data    
# To create the reports
from django.views import View
from .reports import excel_report
# To create maps
import folium
import folium.map


class MainView(TemplateView):
    # Charge the info of the db to the template
    template_name = "dashboard/index.html"
    def get_context_data(self, **kwargs):
        # call the super method that put the base content
        context = super().get_context_data(**kwargs)
        # Add the information into the template
        context.update(get_latest_data())
        return context

class ExportExcelView(View):
    # create a report of the database
    def get(self, request, *args, **kwargs):
        # create the report
        return excel_report()
    
def view_map(request):
    """
    # Llama a la función get_latest_data()
    latest_data = get_latest_data()
    # if it has registers
    if latest_data['objects']:
        first_object = latest_data['objects'][0]
        position = first_object['position']  # There you've got the location
        #convert it to numbers
        lat, lng = map(float, position.split(' '))
        # Crete the map
        mapa = folium.Map(location=[lat, lng], zoom_start=13)
        # Add a flag
        folium.Marker([lat, lng], popup="Ubicación del Sensor").add_to(mapa)
        # Generate the html
        mapa_html = mapa._repr_html_()
        # Renderiza la plantilla con el mapa
        return render(request, 'dashboard/maps.html', {'mapa': mapa_html})
    else:
        # Manejar el caso donde no hay datos en 'objects'
        mapa = folium.Map(location=[4.690347, -74.067436], zoom_start=13)
        # Add a flag
        folium.Marker([4.690347, -74.067436], popup="Andes's offices").add_to(mapa)
        # Generate the html
        mapa_html = mapa._repr_html_()
        return render(request, 'dashboard/maps.html', {'mapa': mapa_html})
    """
    
        # Crete the map
    lat = 4.698446
    lng = -74.105120
    mapa = folium.Map(location=[lat, lng], zoom_start=13)
    # Add a flag
    folium.Marker([lat, lng], popup="Ubicación del Sensor").add_to(mapa)
    # Generate the html
    mapa_html = mapa._repr_html_()
    # Renderiza la plantilla con el mapa
    return render(request, 'dashboard/maps.html', {'mapa': mapa_html})
    
def simple_form(request):
    # it's wrong!
    return render(request, './forms/asign_sensor.html')

# api views

def view_sensor_data(request): # si pones *args **kwgars, el id se guarda ahí...
    # Instance of the json received from the api (clase 13 platzi)
    processed_data = process_sensor_data() # si se le pide el parametro, solo te va a actualizar los que necesitas
    return render(request, 'api/load_data.html', {'processed_data': processed_data})
