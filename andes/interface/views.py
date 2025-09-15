from django.views.generic.base import TemplateView
from django.views.generic import ListView, DeleteView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Empresa
from accounts.models import Usuario, Operador
from django.shortcuts import redirect
from typing import cast

from .utils import get_latest_data, compare_dates
from django.shortcuts import render
from django.urls import reverse_lazy
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

# ====== api views ========

def view_sensor_data(request): # si pones *args **kwgars, el id se guarda ahí...
    # Instance of the json received from the api (clase 13 platzi)
    processed_data = process_sensor_data() # si se le pide el parametro, solo te va a actualizar los que necesitas
    return render(request, 'api/load_data.html', {'processed_data': processed_data})

# ====== interface views ========

def view_compare(request):
    #each minute, evaluate if can register the data.
    response_message = compare_dates()
    return render(request, 'variables_updated.html', {'status': response_message})


# ========= Menu views ============

class MenuEmpView(LoginRequiredMixin, TemplateView):
    template_name = 'menu/empresa.html'

    def dispatch(self, request, *args, **kwargs):
        user = cast(Usuario, request.user)
        if not Empresa.objects.filter(usuario_id=user.pk).exists():
            return redirect('users:login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = cast(Usuario, self.request.user)
        context['user_id'] = user.pk
        context['user_name'] = user.get_full_name() 
        context['empresa'] = Empresa.objects.filter(usuario_id=user.pk).first()
        return context
    
class MenuFactView(LoginRequiredMixin, TemplateView):
    template_name = 'menu/admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = cast(Usuario, self.request.user)
        context['user_id'] = user.pk
        context['user_name'] = user.get_full_name() 
        context['user'] = user
        return context
    
# ========= operador gest ===========

