
from django import forms
from ..models import Empresa, ServerCredentials

W = {"class": "w-full px-3 py-2 rounded border dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"}

class SensorTPForm(forms.Form):
    # Sensor
    nombre = forms.CharField(
        max_length=45, required=False, label="Nombre",
        widget=forms.TextInput(attrs= W | {"placeholder": "Nombre del sensor"})
    )
    estado = forms.BooleanField(
        required=False, label="¿Activo?",
        widget=forms.CheckboxInput(attrs={"class": "h-4 w-4 rounded border"})
    )
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.all(), required=False, label="Empresa",
        widget=forms.Select(attrs=W)
    )

    # GasRestante
    localizacion = forms.CharField(
        max_length=45, required=False, label="Localización",
        widget=forms.TextInput(attrs= W | {"placeholder": "Sala / Equipo / Ubicación"})
    )
    bateria = forms.CharField(
        max_length=45, required=False, label="Batería",
        widget=forms.TextInput(attrs= W | {"placeholder": "Ej. 85%"})
    )
    toleranciaMins = forms.IntegerField(
        required=False, label="Tolerancia de tiempo (mins)",
        widget=forms.NumberInput(attrs= W | {"placeholder": "Tolerancia en minutos"})
    )
    server_deviceNo = forms.CharField(
        max_length=85, required=False, label="Device No (servidor)",
        widget=forms.TextInput(attrs= W | {"placeholder": "Número de dispositivo en servidor"})
    )
    server_credentials = forms.ModelChoiceField(
        queryset=ServerCredentials.objects.all(), required=True, label="Credenciales del servidor",
        empty_label="(selecciona credencial)",
        widget=forms.Select(attrs=W)
    )
