from django.urls import path
from .views import *

app_name = 'users'
urlpatterns = [
    path('login/', CustomLoginView.as_view(), name = "login"),
    path('register/', SignUpEmpView.as_view(), name = "register"),
    path('signout/', CustomLogoutView.as_view(), name = "signout"),
    path('profile/', CustomLogoutView.as_view(), name = "profile"),
    # operador gests
    path("emp_list", OperadorListView.as_view(), name="empList"),
    path("create_op", OperadorCreateView.as_view(), name="createEmp"),
    path("update_op/<int:pk>/update", OperadorUpdateView.as_view(), name="updateEmp"),
    path("delete_op/<int:pk>/", OperadorDeleteView.as_view(), name="deleteEmp"),
    # empresa gests
    path("empresa_list", EmpresaListView.as_view(), name="FactList"),
    path('empresa/<int:pk>/edit/', EmpresaUpdateView.as_view(), name='updateEmpresa'),
    path('empresa/<int:pk>/delete/', EmpresaDeleteView.as_view(), name='deleteEmpresa'),
]