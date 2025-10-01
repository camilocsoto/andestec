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
    path('operator_menu/', MenuOperatorView.as_view(), name='OperatorMenu'),
    # ticket gests
    path('ticket/', TicketListView.as_view(), name='ticketList'),
    path('ticket/create', TicketCreateView.as_view(), name='ticket_create'),
    path("ticket/<int:pk>/", TicketDetailView.as_view(), name="ticket_detail"),
    path("ticket/<int:pk>/add_message/", MessageCreateView.as_view(), name="ticket_add_message"),
    path("ticket/<int:pk>/update_state/", TicketEstadoUpdateView.as_view(), name="ticket_update_state"),
    path("ticket/<int:pk>/download/", TicketDownloadView.as_view(), name="ticket_download"),
    
]