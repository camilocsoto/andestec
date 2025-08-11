from django.urls import path
from .views import *

app_name = 'users'
urlpatterns = [
    path('login/', CustomLoginView.as_view(), name = "login"),
    path('register/', SignUpView.as_view(), name = "register"),
]