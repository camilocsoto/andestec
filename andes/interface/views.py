from django.views.generic.base import TemplateView
from .utils import get_latest_data
from dashboard.models import Variable
# To create the reports
from django.http import HttpResponse
from django.views import View
from openpyxl import Workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import os

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
        """
        Add an image to the report, the logo of Andes.
        Add styles to the table
        Add the information to the table
        """
        # Ceate a new workbook file in excel
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Report Data"

        # set the image and his propierties
        image_path = os.path.join('./interface/static/dist/images/andes_tec.png')
        img = OpenpyxlImage(image_path)
        img.height = 92
        img.width = 390
        worksheet.add_image(img, 'A1')  # 'A1' is the field where the image will be add

        # set styles to the headers row
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        thin_border = Border(left=Side(style='thin'), 
                             right=Side(style='thin'), 
                             top=Side(style='thin'), 
                             bottom=Side(style='thin'))
        # set the names of the columns
        headers = [
            'ID', 'Sensor Name', 'Time', 'Temperature (°C)', 
            'Pressure (psi)',  'Output Force (%)', 'Litres (L)', 'Percentage of Gas (%)'
        ]
        # add enough space to the image and add it
        worksheet.append([''] * len(headers))
        worksheet.append([''] * len(headers))
        worksheet.append([''] * len(headers))
        worksheet.append([''] * len(headers))
        worksheet.append([''] * len(headers))
        worksheet.append(headers)

        # set the styles for the space of the html
        for col_num, header in enumerate(headers, start=1):
            cell = worksheet.cell(row=6, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border

        # get the data of the table Variable
        variables = Variable.objects.select_related('sensors_sen_id').order_by('-id')

        # Agrega los datos al Excel
        for variable in variables:
            # Obtén el sensor asociado
            sensor = variable.sensors_sen_id
            worksheet.append([
                variable.id,
                sensor.sen_name,
                variable.var_time.strftime("%Y-%m-%d %H:%M:%S"),
                variable.var_temperature,
                variable.var_presure, # Current pressure in psi detected by the sensor
                variable.var_output_capacity, # % of pressure in psi
                variable.var_litres,
                variable.var_current_capacity, # % of gas in litres 
            ])
            # set styles to rows of the data
            for row in worksheet.iter_rows(min_row=7, max_row=worksheet.max_row, min_col=1, max_col=len(headers)):
                for cell in row:
                    cell.border = thin_border

            # Adjust the size of the fields
            for col in range(1, len(headers) + 1):
                column_letter = get_column_letter(col)
                worksheet.column_dimensions[column_letter].width = 15
        # Prepare the download of the file
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=datos_cilindro_{sensor.sen_id}.xlsx'
        # Guarda el workbook en la respuesta
        workbook.save(response)

        return response
