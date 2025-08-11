from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from .forms import AuthForm, UserForm
from .models import Usuario, Empresa, Operador
from typing import cast

class SignUpView(CreateView):
    form_class = UserForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('accounts:login')

class CustomLoginView(LoginView):
    authentication_form = AuthForm
    template_name = 'registration/login.html'
    def get_success_url(self):
        user = cast(User, self.request.user)
        # redirige a la vista correspondiente según el rol del usuario
        if user.rol == 1:
            return reverse_lazy('app:select_tipo')
        elif user.rol == 2:
            return reverse_lazy('app:ticket_list')
        elif user.rol == 3:
            return reverse_lazy('app:ticket_list')
        elif user.rol == 4:
            return reverse_lazy('app:select_tipo')        
        return super().get_success_url()
    
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')