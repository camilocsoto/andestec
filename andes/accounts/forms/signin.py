from django import forms
from typing import cast
from accounts.models import Empresa, Rol, Usuario
from django.contrib.auth.hashers import make_password

class EmpresaRegistroForm(forms.ModelForm):
    TIPO_PERSONA_CHOICES = [
        ('natural', 'Natural'),
        ('jurídica', 'Jurídica'),
    ]
    
    tipo_persona = forms.ChoiceField(choices=TIPO_PERSONA_CHOICES, label="Tipo de Persona")
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellido", max_length=150, required=False)

    email = forms.EmailField(label="Correo electrónico")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = Empresa
        fields = [
            'tipo_persona',
            'first_name',
            'last_name',
            'email',
            'password',
            'password_confirm'            
        ]

    def __init__(self, *args, **kwargs):
        tipo_persona_seleccionada = None
        if 'data' in kwargs:
            tipo_persona_seleccionada = kwargs['data'].get('tipo_persona')
        super().__init__(*args, **kwargs)

        # Si es jurídica, ocultar last_name
        if tipo_persona_seleccionada == "jurídica":
                self.fields['last_name'].required = False
                self.fields['last_name'].widget = forms.HiddenInput()
                
    def save(self, commit=True):
        usuario = Usuario(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data.get('last_name', ''),
            email=self.cleaned_data['email'],
            rol=Rol.objects.get(pk=2)
        )
        usuario.password = make_password(self.cleaned_data['password'])
        usuario.save()

        # ahora crear Empresa vinculada a ese usuario
        empresa = super().save(commit=False)
        empresa.usuario = usuario
        if commit:
            empresa.save()
        return empresa