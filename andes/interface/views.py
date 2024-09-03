from django.views.generic.base import TemplateView
from .utils import get_latest_data
from dashboard.models import Variable
from django.http import HttpResponse
from django.views import View
from openpyxl import Workbook

class MainView(TemplateView):
    template_name = "dashboard/index.html"
    """
    Need to get the id of the sensor.
    Need to generate the reports
    """
    def get_context_data(self, **kwargs):
        # call the super method that put the base content
        context = super().get_context_data(**kwargs)
        # Add the information into the template
        context.update(get_latest_data())
        
        return context

class ExportExcelView(View):
    def get(self, request, *args, **kwargs):
        # Crea un nuevo workbook
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Variables Data"

        # Especifica los encabezados
        headers = [
            'Temperature', 'Signal', 'Pressure', 'Time', 'Output Force',
            'Percentage of Gas', 'Litres', 'Battery', 'Location', 
            'Sensor ID', 'Sensor Name', 'Max Masa', 'Max Output Force'
        ]
        worksheet.append(headers)

        # Obtén los datos del modelo Variable
        variables = Variable.objects.select_related('sensors_sen_id').all()

        # Agrega los datos al Excel
        for variable in variables:
            # Obtén el sensor asociado
            sensor = variable.sensors_sen_id
            worksheet.append([
                variable.var_temperature,
                variable.var_radiofrecuency,
                variable.var_presure,
                variable.var_time.strftime("%Y-%m-%d %H:%M:%S"),
                variable.var_output_capacity,
                variable.var_current_capacity,
                variable.var_litres,
                variable.var_battery,
                variable.localizacion,
                sensor.sen_id,  # ID del sensor
                sensor.sen_name,  # Nombre del sensor
                sensor.max_masa,  # Masa máxima permitida
                sensor.max_output_force,  # Fuerza máxima de salida
            ])

        # Prepara la respuesta como archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=datos_cilindro_{sensor.sen_id}.xlsx'

        # Guarda el workbook en la respuesta
        workbook.save(response)

        return response