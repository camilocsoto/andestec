from django.urls import path
from .views import *

app_name = 'users'
urlpatterns = [
    path('login/', CustomLoginView.as_view(), name = "login"),
    path('register/', SignUpEmpView.as_view(), name = "register"),
    path('signout/', CustomLogoutView.as_view(), name = "signout"),
    path('profile/', CustomLogoutView.as_view(), name = "profile"),
]