from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from .forms import AuthForm, EmpresaRegistroForm, OperadorCreateForm
from .models import Usuario, Empresa, Operador
from django.views.generic import ListView, DeleteView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from typing import cast
from django.http import HttpResponseRedirect

class SignUpEmpView(CreateView):
    form_class = EmpresaRegistroForm
    template_name = 'authentication/sign-up.html'
    success_url = reverse_lazy('users:login')

class CustomLoginView(LoginView):
    authentication_form = AuthForm
    template_name = 'authentication/sign-in.html'
    def get_success_url(self):
        user = cast(Usuario, self.request.user)
        if not user.rol:
            return super().get_success_url()
        # redirige a la vista correspondiente según el rol del usuario
        match user.rol.pk:
            case 1:
                return reverse_lazy('app:compare')
            case 2:
                return reverse_lazy('app:emp_menu')
            case 3:
                return reverse_lazy('app:compare')  
        return super().get_success_url()
    
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')

class CustomProfileView(TemplateView):
    template_name = 'dashboard/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = cast(Usuario, self.request.user)
        context['user'] = user
        if user.rol == 2:  # Si es empresa
            context['empresa'] = Empresa.objects.get(usuario=user)
        elif user.rol == 3:  # Si es operador
            context['operador'] = Operador.objects.get(usuario=user)
        return context    

# operator crud views:

class OperadorListView(LoginRequiredMixin, ListView):
    template_name = "operario/empresa-emp.html"
    model = Operador
    context_object_name = "operadores"

    def get_queryset(self):
        user = cast(Usuario, self.request.user)
        empresa = Empresa.objects.filter(usuario_id=user.pk).first()
        return Operador.objects.filter(empresa=empresa).select_related("usuario")
    
    
class OperadorCreateView(LoginRequiredMixin, CreateView):
    template_name = "operario/create_op.html"
    model = Usuario
    form_class = OperadorCreateForm

    def form_valid(self, form):
        # obtener empresa del usuario logueado
        try:
            empresa = Empresa.objects.get(usuario_id=self.request.user.pk)
        except Empresa.DoesNotExist:
            form.add_error(None, "No se encontró la empresa asociada al usuario actual.")
            return self.form_invalid(form)

        try:
            usuario = form.save(empresa=empresa) # error = no parameter named "empresa"
        except Exception as e:
            form.add_error(None, f"Error al crear el operador: {e}")
            return self.form_invalid(form)

        # CreateView espera que self.object sea la instancia creada
        self.object = usuario
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("app:emp_menu")


class OperadorUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "operadores/form.html"
    model = Usuario
    fields = ["first_name", "last_name", "email", "numDocumento"]

    def get_success_url(self):
        return reverse_lazy("app:emp_menu")


class OperadorDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "operadores/confirm_delete.html"
    model = Usuario

    def get_success_url(self):
        return reverse_lazy("operadores:listar")
