import os
from openpyxl import Workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from dashboard.models import Variable

def excel_report():
    """
        Add an image to the report, the logo of Andes.
        Add styles to the table
        Add the information to the table
        """
    # Crear el archivo Excel
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Report Data"

    # Establecer la imagen del logo
    image_path = os.path.join('./interface/static/dist/img/andes_tec.png')
    img = OpenpyxlImage(image_path)
    img.height = 92
    img.width = 390
    worksheet.add_image(img, 'A1')  # 'A1' es donde se añadirá la imagen

    # Estilos para la cabecera
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                         top=Side(style='thin'), bottom=Side(style='thin'))

    # Nombres de las columnas
    headers = [
        'Id', 'Sensor name', 'Time', 'Temperature (°C)',
        'Pressure (psi)', 'Pressure (%)', 'Quantity of gas (L)', 'Percentage of gas (%)'
    ]

    # Añadir espacio para la imagen y después las cabeceras
    worksheet.append([''] * len(headers))
    worksheet.append([''] * len(headers))
    worksheet.append([''] * len(headers))
    worksheet.append([''] * len(headers))
    worksheet.append([''] * len(headers))
    worksheet.append(headers)

    # Aplicar estilos a la cabecera
    for col_num, header in enumerate(headers, start=1):
        cell = worksheet.cell(row=6, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    # Obtener datos de la tabla Variable
    variables = Variable.objects.select_related('sensors_sen_id').order_by('-id')

    # Añadir los datos al Excel
    for variable in variables:
        sensor = variable.sensors_sen_id
        worksheet.append([
            variable.id,
            sensor.sen_name,
            variable.var_time.strftime("%Y-%m-%d %H:%M:%S"),
            variable.var_temperature,
            variable.var_presure,
            variable.var_output_capacity,
            variable.var_litres,
            variable.var_current_capacity,
        ])
        # Aplicar estilos a las filas de datos
        for row in worksheet.iter_rows(min_row=7, max_row=worksheet.max_row, min_col=1, max_col=len(headers)):
            for cell in row:
                cell.border = thin_border

    # Ajustar el tamaño de las columnas
    for col in range(1, len(headers) + 1):
        column_letter = get_column_letter(col)
        worksheet.column_dimensions[column_letter].width = 15

    # Preparar la respuesta para descargar el archivo
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=datos_cilindro_{sensor.sen_id}.xlsx'
    # Guardar el workbook en la respuesta
    workbook.save(response)
    return response
