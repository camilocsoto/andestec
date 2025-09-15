from django.urls import path
from .views import *

app_name = 'app'
urlpatterns = [
    path('device/<int:id>', MainView.as_view(), name='device_view'),
    path('download/', ExportExcelView.as_view()),
    path('maps/', view_map, name='view_map' ),
    path('asign/', simple_form, name='asign_sensor'),
    path('load_data/', view_sensor_data),
    path('compare/', view_compare, name='compare'), 
    path('employee_menu/', MenuEmpView.as_view(), name='emp_menu'),
    path('factory_menu/', MenuFactView.as_view(), name='factoryMenu'),
]