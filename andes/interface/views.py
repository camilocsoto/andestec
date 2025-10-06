from django.views.generic.base import TemplateView
from django.views.generic import ListView, DeleteView, CreateView, UpdateView, DetailView, View, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Empresa, Usuario, Operador
from interface.models import TcketSoporte, Mensaje, ComposicionGas, ServerCredentials, TipoSensor, CaracteristicasCilindro, Sensor
from interface.forms.gas_comp import ComposicionGasForm
from interface.forms.messages import MessageForm
from interface.forms.tickets import TicketSoporteForm
from interface.forms.update_ticket import EstadoTicketForm
from interface.forms.tipo_sensor import TipoSensorForm
from interface.forms.server_cred import ServerCredentialsForm
from interface.forms.cylinders import CaracteristicasCilindroForm
from interface.services.sensor import SensorService
from interface.strategies.sensor import SensorStrategy
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.db.models import Case, When, Value, BooleanField
from django.db.models.query import QuerySet
from django.contrib import messages
from django.utils import timezone
from typing import cast, Optional
import mimetypes
from .utils import get_latest_data, compare_dates
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from .adapters import process_sensor_data    
# To create the reports
from django.views import View
from .reports import excel_report
# To create maps
import folium
import folium.map

    # Mapas para persistir y mostrar
ESTADO_TO_BYTES = {
        'abierto': b'\x00',
        'en_proceso': b'\x02',
        'cerrado': b'\x01',
}

BYTES_TO_ESTADO = {v: k for k, v in ESTADO_TO_BYTES.items()}

ESTADO_LABELS = {
    None: "Pendiente",
    b'\x00': "Abierto",
    b'\x02': "En proceso",
    b'\x01': "Cerrado",
}


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

class MainMenuView(LoginRequiredMixin, TemplateView):
    template_name = "menu/main_menu.html"

    def dispatch(self, request, *args, **kwargs):
        # (opcional) redirigir si no tiene rol o no está completo su perfil
        user = cast(Usuario, request.user)
        # Si quieres bloquear usuarios sin rol, puedes descomentar:
        # if not getattr(user, "rol_id", None):
        #     return redirect("users:login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = cast(Usuario, self.request.user)
        role_id = getattr(user, "rol_id", None)

        # flags
        is_admin = role_id == 1
        # si existe Empresa asociada por usuario (dueño) consideramos "empresa"
        empresa = Empresa.objects.filter(usuario_id=user.pk).first()
        is_empresa = bool(empresa) or role_id == 2

        operador = Operador.objects.filter(usuario_id=user.pk).select_related("empresa__usuario").first()
        is_operador = bool(operador) or role_id == 3

        context.update({
            "user": user,
            "user_name": user.get_full_name(),
            "role_id": role_id,
            "is_admin": is_admin,
            "is_empresa": is_empresa,
            "is_operador": is_operador,
            "empresa": empresa,
            "operador": operador,
        })
        return context

class MenuAdminView(LoginRequiredMixin, TemplateView):
    template_name = 'menu/admin_services.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = cast(Usuario, self.request.user)
        context['user_id'] = user.pk
        context['user_name'] = user.get_full_name() 
        context['user'] = user
        return context

class MenuAdminSettingsView(LoginRequiredMixin, TemplateView): 
    template_name = 'menu/admin_settings.html' 
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs) 
        user = cast(Usuario, self.request.user) 
        context['user_id'] = user.pk 
        context['user_name'] = user.get_full_name() 
        context['user'] = user 
        return context


# ========= ticket gest ===========

class TicketListView(LoginRequiredMixin, ListView):
    model = TcketSoporte
    template_name = "tickets/ticket_list.html"
    context_object_name = "tickets"

    def get_queryset(self):
        user = cast(Usuario, self.request.user)
        rol_id = getattr(user, "rol_id", None)

        # queryset base con relaciones para evitar N+1
        qs = TcketSoporte.objects.select_related("empresa__usuario", "TipoPeticion").order_by("-fecha_creacion")

        # Admin (rol 1): ver todas las peticiones EXCLUYENDO las cuyo estado == 1 (b'\x01')
        if rol_id == 1:
            # Excluir los que tengan estado == 1 (asumimos que 1 -> b'\x01')
            return qs.exclude(estado=b'\x01')

        # Roles 2 y 3: ver solo los tickets de la empresa asociada al operador (si existe)
        if rol_id in (2, 3):
            operador = Operador.objects.filter(usuario_id=user.pk).first()
            if operador and operador.empresa:
                return qs.filter(empresa_id=operador.empresa.pk)

            # fallback: si no es operador, tal vez es el dueño de la empresa (usuario_empresa)
            empresa = Empresa.objects.filter(usuario_id=user.pk).first()
            if empresa:
                return qs.filter(empresa=empresa)

            # sin empresa conocida -> no mostrar nada
            return TcketSoporte.objects.none()

        # otros roles -> no ver nada por defecto
        return TcketSoporte.objects.none()


class TicketCreateView(LoginRequiredMixin, CreateView):
    form_class = TicketSoporteForm
    template_name = "tickets/ticket_form.html"
    success_url = reverse_lazy("app:ticketList")  # deja como estaba

    def dispatch(self, request, *args, **kwargs):
        # permiso: usuario debe tener rol 3 (según tu regla)
        if getattr(request.user, "rol_id", None) != 3:
            raise PermissionDenied("No tienes permisos para crear un PQRS.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # debug rápido: comprobar form.is_valid() y cleaned_data
        if not form.is_valid():
            messages.error(self.request, "El formulario no es válido.")
            print("FORM ERRORS:", form.errors.as_json())
            return self.form_invalid(form)

        print("DEBUG: form.cleaned_data keys:", list(form.cleaned_data.keys()))
        print("DEBUG: cleaned_data preview:", {k: (type(v).__name__ if k == "archivo" else v) for k, v in form.cleaned_data.items()})

        # buscar el operador del usuario logueado
        operador = Operador.objects.filter(usuario_id=self.request.user.pk).first()
        if not operador:
            # mostrar info en consola y mensaje
            messages.error(self.request, "No se encontró el operario asociado al usuario.")
            return self.form_invalid(form)

        empresa = operador.empresa
        if not empresa:
            messages.error(self.request, "El operario no tiene una empresa asociada.")
            return self.form_invalid(form)

        try:
            # Intentar guardar y capturar el ticket devuelto
            ticket = form.save(commit=False)
            ticket.empresa = empresa
            if getattr(ticket, "pk", None) is None:
                # no se creó
                messages.error(self.request, "El ticket no se guardó (no se devolvió PK). Revisa logs.")
                return self.form_invalid(form)

            messages.success(self.request, "PQRS creado correctamente.")
            self.object = ticket
            return HttpResponseRedirect(self.get_success_url())

        except Exception as e:
            # hacer dump completo del traceback en consola para depuración
            messages.error(self.request, f"Error al crear el PQRS: {e}")
            form.add_error(None, f"Error al crear el PQRS: {e}")
            return self.form_invalid(form)
        
class TicketDetailView(LoginRequiredMixin, DetailView):
    model = TcketSoporte
    template_name = "tickets/ticket_detail.html"
    context_object_name = "ticket"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket: TcketSoporte = cast(TcketSoporte, self.get_object()) 
        # Nombre de la empresa (empresa.usuario es el usuario dueño)
        empresa_name = None
        try:
            empresa_name = ticket.empresa.usuario.get_full_name() or ticket.empresa.usuario.email
        except Exception:
            empresa_name = str(ticket.empresa)
        context["empresa_name"] = empresa_name
        # estado legible
        estado_bytes = ticket.estado  # puede ser None o bytes
        # etiqueta legible
        context["estado_label"] = ESTADO_LABELS.get(estado_bytes, "Desconocido")
        # valor lógico ('abierto'|'en_proceso'|'cerrado'|'pendiente')
        if estado_bytes is None:
            estado_value = 'pendiente'
        else:
            estado_value = BYTES_TO_ESTADO.get(estado_bytes, 'abierto')
        # añadimos al contexto la variante segura
        context['estado_value'] = estado_value
        # si tiene adjunto (binary) lo indicamos
        context["has_attachment"] = bool(ticket.archivos_comprimidos)
        
        # Mensajes relacionados (orden ascendente por timestamp)
        mensajes = Mensaje.objects.filter(TcketSoporte=ticket).order_by('timestamp')
        context['mensajes'] = mensajes

        # Form para agregar mensaje y actualizar el estado
        context['message_form'] = MessageForm()
        # si viene 'pendiente' inicializamos en 'abierto' para el select
        initial_estado = 'abierto' if estado_value == 'pendiente' else estado_value
        context['estado_form'] = EstadoTicketForm(initial={'estado': initial_estado})

        return context

class MessageCreateView(LoginRequiredMixin, View):
    """
    Vista que crea el mensaje con Usuario=request.user y TcketSoporte=ticket,
    y redirige al ticket_detail.
    """
    def post(self, request, pk, *args, **kwargs):
        ticket = get_object_or_404(TcketSoporte, pk=pk)
        form = MessageForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            # Asignar usuario y ticket
            mensaje.Usuario = request.user
            mensaje.TcketSoporte = ticket
            mensaje.save()
            # redirigir al detalle del ticket
            return redirect('app:ticket_detail', pk=ticket.pk)
        # si no es válido, volvemos al detail rendering con errores:
        # Aquí re-renderizamos directamente para mostrar errores:
        context = {
            'ticket': ticket,
            'empresa_name': ticket.empresa.usuario.get_full_name() if ticket.empresa and ticket.empresa.usuario else str(ticket.empresa),
            'estado_label': ("Pendiente" if ticket.estado is None else ("Cerrado" if ticket.estado == b'\x01' else "Abierto")),
            'has_attachment': bool(ticket.archivos_comprimidos),
            'mensajes': Mensaje.objects.filter(TcketSoporte=ticket).order_by('timestamp'),
            'message_form': form
        }

class TicketEstadoUpdateView(LoginRequiredMixin, View):
    """
    Recibe POST en /ticket/<pk>/update_state/ y actualiza solo ticket.estado y fecha_actualizacion,
    luego redirige al ticket_detail.
    """

    def post(self, request, pk, *args, **kwargs):
        ticket = get_object_or_404(TcketSoporte, pk=pk)

        # permiso en el servidor: solo roles 1 o 2
        user_rol_id = getattr(request.user, 'rol_id', None)
        if user_rol_id not in (1, 2):
            # opcional: 403 o redirigir con mensaje
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permiso para cambiar el estado.")

        form = EstadoTicketForm(request.POST)
        if form.is_valid():
            estado_choice = form.cleaned_data['estado']  # 'abierto'|'en_proceso'|'cerrado'
            # mapear al byte correspondiente
            byte_val = ESTADO_TO_BYTES.get(estado_choice)
            ticket.estado = byte_val
            ticket.fecha_actualizacion = timezone.now()
            ticket.save(update_fields=['estado', 'fecha_actualizacion'])
            return redirect('app:ticket_detail', pk=ticket.pk)

        # si no válido, re-renderizamos el detalle con el form con errores
        mensajes = Mensaje.objects.filter(TcketSoporte=ticket).order_by('timestamp')
        context = {
            'ticket': ticket,
            'empresa_name': ticket.empresa.usuario.get_full_name() if ticket.empresa and ticket.empresa.usuario else str(ticket.empresa),
            'estado_label': ESTADO_LABELS.get(ticket.estado, "Desconocido"),
            'has_attachment': bool(ticket.archivos_comprimidos),
            'mensajes': mensajes,
            'message_form': MessageForm(),
            'estado_form': form
        }
        return render(request, "tickets/ticket_detail.html", context)

class TicketDownloadView(LoginRequiredMixin, View):
    """
    Devuelve el contenido de 'archivos_comprimidos' para un ticket.
    Convierte memoryview/bytearray a bytes y detecta tipo por firma (png/jpg/pdf/xlsx).
    """
    def get(self, request, pk, *args, **kwargs):
        ticket = get_object_or_404(TcketSoporte, pk=pk)

        raw = ticket.archivos_comprimidos
        if not raw:
            raise Http404("No hay archivo para descargar.")

        # Normalizar a bytes (soportar memoryview, bytearray, bytes, etc.)
        try:
            if isinstance(raw, memoryview):
                data = raw.tobytes()
            elif isinstance(raw, bytearray):
                data = bytes(raw)
            elif isinstance(raw, bytes):
                data = raw
            else:
                # intento genérico (por si el driver DB devuelve otro tipo)
                data = bytes(raw)
        except Exception:
            raise Http404("Formato de archivo almacenado no reconocido.")

        # detectar por firma (magic numbers) con slices en bytes
        content_type = "application/octet-stream"
        filename = f"ticket_{ticket.pk}_attachment.bin"

        head4 = data[:4]  # suficiente para las firmas que usamos

        if head4.startswith(b"\x89PNG"):
            content_type = "image/png"
            filename = f"ticket_{ticket.pk}.png"
        elif data[:2] == b"\xff\xd8":
            content_type = "image/jpeg"
            filename = f"ticket_{ticket.pk}.jpg"
        elif data[:4] == b"%PDF":
            content_type = "application/pdf"
            filename = f"ticket_{ticket.pk}.pdf"
        elif head4 == b'PK\x03\x04':  # xlsx/docx/zip container
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"ticket_{ticket.pk}.xlsx"
        else:
            guessed, _ = mimetypes.guess_type(filename)
            content_type = guessed or content_type

        resp = HttpResponse(data, content_type=content_type)
        resp["Content-Length"] = str(len(data))
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp
    
    
# ========= gas properties ===========

class ComposicionGasListView(LoginRequiredMixin, ListView):
    model = ComposicionGas
    template_name = "cruds/gas_composition/gas_comp_list.html"
    context_object_name = "composiciones"

    def get_queryset(self):
        return ComposicionGas.objects.all().order_by('nombre')

class ComposicionGasCreateView(LoginRequiredMixin, CreateView):
    model = ComposicionGas
    form_class = ComposicionGasForm
    template_name = "cruds/gas_composition/gas_comp_create.html"
    success_url = reverse_lazy("app:composiciongas_list") 
    
class ComposicionGasUpdateView(LoginRequiredMixin, UpdateView):
    model = ComposicionGas
    form_class = ComposicionGasForm
    template_name = "cruds/gas_composition/gas_comp_update.html"
    success_url = reverse_lazy("app:composiciongas_list")
    
class ComposicionGasDeleteView(LoginRequiredMixin, DeleteView):
    model = ComposicionGas
    template_name = "cruds/gas_composition/gas_comp_delete.html"
    context_object_name = "composicion"
    success_url = reverse_lazy("app:composiciongas_list")
    
# ========= tipo de sensores ===========

class TipoSensorListView(LoginRequiredMixin, ListView):
    model = TipoSensor
    template_name = "cruds/tipo_sensores/tipo_sen_list.html"
    context_object_name = "tipos"

    def get_queryset(self):
        return TipoSensor.objects.all().order_by('nombre')


class TipoSensorCreateView(LoginRequiredMixin, CreateView):
    model = TipoSensor
    form_class = TipoSensorForm
    template_name = "cruds/tipo_sensores/tipo_sen_create.html"
    success_url = reverse_lazy("app:tiposensor_list")
    
    
class TipoSensorUpdateView(LoginRequiredMixin, UpdateView):
    model = TipoSensor
    form_class = TipoSensorForm
    template_name = "cruds/tipo_sensores/tipo_sen_update.html"
    context_object_name = "tipo"
    success_url = reverse_lazy("app:tiposensor_list")


class TipoSensorDeleteView(LoginRequiredMixin, DeleteView):
    model = TipoSensor
    template_name = "cruds/tipo_sensores/tipo_sen_delete.html"
    context_object_name = "tipo"
    success_url = reverse_lazy("app:tiposensor_list")

# ========= server properties ===========

class ServerCredentialsListView(LoginRequiredMixin, ListView):
    model = ServerCredentials
    template_name = "cruds/servidores/servidores_list.html"
    context_object_name = "credentials"

    def get_queryset(self):
        return ServerCredentials.objects.all().order_by('nombre')

class ServerCredentialsCreateView(LoginRequiredMixin, CreateView):
    model = ServerCredentials
    form_class = ServerCredentialsForm
    template_name = "cruds/servidores/servidores_create.html"
    success_url = reverse_lazy("app:servercredentials_list")
    
class ServerCredentialsUpdateView(LoginRequiredMixin, UpdateView):
    model = ServerCredentials
    form_class = ServerCredentialsForm
    template_name = "cruds/servidores/servidores_update.html"
    context_object_name = "credential"
    success_url = reverse_lazy("app:servercredentials_list")

    def form_valid(self, form):
        # Si el password viene vacío en el formulario de edición, conservamos el valor anterior en la BD.
        password = form.cleaned_data.get('password')
        if password in (None, ''):
            # recuperar el objeto original desde la BD apto para pylance
            original = cast(ServerCredentials, self.get_object()) 
            form.instance.password = original.password
        return super().form_valid(form)

class ServerCredentialsDeleteView(LoginRequiredMixin, DeleteView):
    model = ServerCredentials
    template_name = "cruds/servidores/servidores_delete.html"
    context_object_name = "credential"
    success_url = reverse_lazy("app:servercredentials_list")
    
# ========= cylinder properties ===========

class CaracteristicasCilindroListView(LoginRequiredMixin, ListView):
    model = CaracteristicasCilindro
    template_name = "cruds/cilindros/cyl_list.html"
    context_object_name = "caracteristicas"

    def get_queryset(self):
        # ordenar por nombre (ajusta si quieres otro criterio)
        return CaracteristicasCilindro.objects.all().order_by('nombre')

class CaracteristicasCilindroCreateView(LoginRequiredMixin, CreateView):
    model = CaracteristicasCilindro
    form_class = CaracteristicasCilindroForm
    template_name = "cruds/cilindros/cyl_create.html"
    success_url = reverse_lazy("app:caracteristicas_list")
    
class CaracteristicasCilindroUpdateView(LoginRequiredMixin, UpdateView):
    model = CaracteristicasCilindro
    form_class = CaracteristicasCilindroForm
    template_name = "cruds/cilindros/cyl_update.html"
    context_object_name = "caracteristica"
    success_url = reverse_lazy("app:caracteristicas_list")


class CaracteristicasCilindroDeleteView(LoginRequiredMixin, DeleteView):
    model = CaracteristicasCilindro
    template_name = "cruds/cilindros/cyl_delete.html"
    context_object_name = "caracteristica"
    success_url = reverse_lazy("app:caracteristicas_list")
    
# ========= sensors ===========

class SensorListView(LoginRequiredMixin, ListView):
    model = Sensor
    template_name = "sensors/admin_list.html"
    context_object_name = "sensors"

    def get_queryset(self):
        service = SensorService()
        return service.get_all_sensors()

class TipoSensorSelectView(LoginRequiredMixin, ListView):
    # func to choose the type of sensor before creat one
    model = TipoSensor
    template_name = "sensors/admin_choose_create.html"
    context_object_name = "tipos"
    
    
class SensorCreateView(LoginRequiredMixin, FormView):
    """
    Crea sensores con service.sensor -> strategies.sensor ->sensor_repo según tipo_id.
    """
    success_url = reverse_lazy("app:sensors_list")

    def dispatch(self, request, *args, **kwargs):
        self.tipo_id = int(kwargs["tipo_id"])
        self.strategy = SensorStrategy()
        self.cfg = self.strategy.resolve(self.tipo_id)  # {form_class, template_name, repo}
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return self.cfg["form_class"] # <- forms.Form, perfecto para FormView

    def get_template_names(self):
        return [self.cfg["template_name"]]

    def form_valid(self, form):
        service = SensorService()
        # usa el nombre de método que ya tienes en tu service
        sensor = service.create_tpsensor(tipo_id=self.tipo_id, data=form.cleaned_data)
        messages.success(self.request, f"Sensor '{sensor.nombre or sensor.pk}' creado correctamente.")
        # FormView.form_valid redirige a success_url sin intentar form.save()
        return super().form_valid(form)
    

class SensorUpdateView(FormView):
    """
    Edita un sensor existente (y su GasRestante).
    Strategy elige form y template según sensor.tipoSensor.
    """
    success_url = reverse_lazy("app:sensors_list")

    def dispatch(self, request, *args, **kwargs):
        self.sensor_id = int(kwargs["pk"])
        # obtén el tipo del sensor para resolver la strategy
        sensor = Sensor.objects.select_related("tipoSensor").get(pk=self.sensor_id)
        self.tipo_id = sensor.tipoSensor.pk

        self.strategy = SensorStrategy()
        self.cfg = self.strategy.resolve_update(self.tipo_id)  # {form_class, template_name, repo}
        self.service = SensorService()
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return self.cfg["form_class"]

    def get_template_names(self):
        return [self.cfg["template_name"]]

    def get_initial(self):
        return self.service.get_update_initial(sensor_id=self.sensor_id)

    def form_valid(self, form):
        sensor = self.service.update(sensor_id=self.sensor_id, data=form.cleaned_data)
        messages.success(self.request, f"Sensor '{sensor.nombre or sensor.pk}' actualizado.")
        return super().form_valid(form)
    
class SensorDeleteView(DeleteView):
    """
    Confirma y borra un Sensor. view -> service -> repo
    """
    model = Sensor
    template_name = "sensors/admin_delete.html"
    success_url = reverse_lazy("app:sensors_list")
    context_object_name = "sensor"

    def post(self, request, *args, **kwargs):
        # Cargamos para mostrar mensajes bonitos, pero no borramos aquí
        self.object = self.get_object()
        service = SensorService()
        ok = service.delete(sensor_id=self.object.pk)
        if ok:
            messages.success(request, f"Sensor '{self.object.pk}' fue eliminado.")
            return HttpResponseRedirect(self.get_success_url())
        # Si no existía (o falló), levantamos 404 o mensaje de error
        raise Http404("El sensor no existe o no pudo eliminarse.")

class SensorMonitorListView(LoginRequiredMixin, ListView):
    model = Sensor
    template_name = "sensors/client_list.html"
    context_object_name = "sensors"

    def get_user_empresa(self) -> Optional[Empresa]:
        user = self.request.user
        try:
            if getattr(user, "rol_id", None) == 2:
                return getattr(user, "empresa", None)
            if getattr(user, "rol_id", None) == 3:
                operador = Operador.objects.filter(usuario_id=user.pk).select_related("empresa").first()
                return operador.empresa if operador else None
        except Exception:
            return None
        return None

    def get_queryset(self) -> QuerySet:
        empresa = self.get_user_empresa()
        if not empresa:
            return Sensor.objects.none()

        qs = (
            Sensor.objects
            .filter(empresa=empresa)
            .select_related("tipoSensor", "empresa__usuario")
            .annotate(
                is_active=Case(
                    When(estado=b"\x01", then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
        )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["empresa"] = self.get_user_empresa()
        return ctx

class SensorDetailView(TemplateView):
    """
    Muestra el detalle del sensor usando Service + Strategy.
    """
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        if pk is None:
            raise Http404("Falta sensor pk")
        self.sensor_id = int(pk)

        payload = SensorService().build_detail(self.sensor_id)
        self._template_name = payload["template_name"]
        self._context = payload["context"]
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return [self._template_name]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(self._context)
        return ctx
