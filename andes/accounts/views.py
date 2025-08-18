from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from .forms import AuthForm, EmpresaRegistroForm
from .models import Usuario, Empresa, Operador
from typing import cast

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
                return reverse_lazy('app:compare')
            case 3:
                return reverse_lazy('app:compare')  
        return super().get_success_url()
    
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')