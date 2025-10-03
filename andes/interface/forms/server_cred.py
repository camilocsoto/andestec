from django import forms
from interface.models import ServerCredentials

class ServerCredentialsForm(forms.ModelForm):
    class Meta:
        model = ServerCredentials
        fields = [
            'nombre',
            'user',
            'password',
            'authorization',
            'descripcion',
            'server_userId',
            'server_clientId',
            'server_access_token',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 rounded border',
                'placeholder': 'Nombre'
            }),
            'user': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 rounded border',
                'placeholder': 'Usuario'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'w-full px-3 py-2 rounded border',
                'placeholder': 'Contraseña',
                'autocomplete': 'new-password'
            }),
            'authorization': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 rounded border',
                'placeholder': 'Autorización'
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 rounded border',
                'placeholder': 'Descripción breve'
            }),
            'server_userId': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 rounded border',
                'placeholder': 'UserId (ej: u123)'
            }),
            'server_clientId': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 rounded border',
                'placeholder': 'ClientId'
            }),
            'server_access_token': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 rounded border',
                'placeholder': 'Access token'
            }),
        }
        labels = {
            'nombre': 'Nombre',
            'user': 'Usuario',
            'password': 'Contraseña',
            'authorization': 'Autorización',
            'descripcion': 'Descripción',
            'server_userId': 'Server userId',
            'server_clientId': 'Server clientId',
            'server_access_token': 'Server access token',
        }