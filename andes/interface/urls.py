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
    #menus
    path("menu/", MainMenuView.as_view(), name="menu"),
    path('admin_menu/', MenuAdminView.as_view(), name='AdminMenu'),
    path('settings_menu/', MenuAdminSettingsView.as_view(), name='adminSettings'),
    # ticket gests
    path('ticket/', TicketListView.as_view(), name='ticketList'),
    path('ticket/create', TicketCreateView.as_view(), name='ticket_create'),
    path("ticket/<int:pk>/", TicketDetailView.as_view(), name="ticket_detail"),
    path("ticket/<int:pk>/add_message/", MessageCreateView.as_view(), name="ticket_add_message"),
    path("ticket/<int:pk>/update_state/", TicketEstadoUpdateView.as_view(), name="ticket_update_state"),
    path("ticket/<int:pk>/download/", TicketDownloadView.as_view(), name="ticket_download"),
    # gas properties
    path("composicion-gas/", ComposicionGasListView.as_view(), name="composiciongas_list"),
    path("composicion-gas/nueva/", ComposicionGasCreateView.as_view(), name="composiciongas_create"),
    path("composicion-gas/<int:pk>/editar/", ComposicionGasUpdateView.as_view(), name="composiciongas_update"),
    path("composicion-gas/<int:pk>/eliminar/", ComposicionGasDeleteView.as_view(), name="composiciongas_delete"),
    # sensor types
    path("tipo_sensor/", TipoSensorListView.as_view(), name="tiposensor_list"),
    path("tipo_sensor/nuevo/", TipoSensorCreateView.as_view(), name="tiposensor_create"),
    path("tipo_sensor/<int:pk>/editar/", TipoSensorUpdateView.as_view(), name="tiposensor_update"),
    path("tipo_sensor/<int:pk>/eliminar/", TipoSensorDeleteView.as_view(), name="tiposensor_delete"),
    # server credentials
    path("servers_auth/", ServerCredentialsListView.as_view(), name="servercredentials_list"),
    path("servers_auth/nueva/", ServerCredentialsCreateView.as_view(), name="servercredentials_create"),
    path("servers_auth/<int:pk>/editar/", ServerCredentialsUpdateView.as_view(), name="servercredentials_update"),
    path("servers_auth/<int:pk>/eliminar/", ServerCredentialsDeleteView.as_view(), name="servercredentials_delete"),
    # gas cylinders
    path("car_cilindro/", CaracteristicasCilindroListView.as_view(), name="caracteristicas_list"),
    path("car_cilindro/nuevo/", CaracteristicasCilindroCreateView.as_view(), name="caracteristicas_create"),
    path("caracteristicas-cilindro/<int:pk>/editar/", CaracteristicasCilindroUpdateView.as_view(), name="caracteristicas_update"),
    path("caracteristicas-cilindro/<int:pk>/eliminar/", CaracteristicasCilindroDeleteView.as_view(), name="caracteristicas_delete"),
    
]
