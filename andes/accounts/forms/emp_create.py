# operadores/forms.py
from typing import Optional
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.models import Usuario, Operador, Empresa, Rol

# clases comunes para inputs (Tailwind)
INPUT_CLASSES = (
    "block w-full rounded-md border-gray-300 shadow-sm sm:text-sm "
    "focus:ring-indigo-500 focus:border-indigo-500 "
    "dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
)

class OperadorCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": INPUT_CLASSES, "autocomplete": "new-password"})
    )
    password2 = forms.CharField(
        label="Repetir contraseña",
        widget=forms.PasswordInput(attrs={"class": INPUT_CLASSES, "autocomplete": "new-password"})
    )
    cargo = forms.CharField(
        label="Cargo",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": INPUT_CLASSES})
    )

    class Meta:
        model = Usuario
        fields = ["first_name", "last_name", "email", "numDocumento"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # aplicar clases a los campos definidos en Meta
        for fname in ("first_name", "last_name", "email", "numDocumento"):
            if fname in self.fields:
                self.fields[fname].widget.attrs.update({"class": INPUT_CLASSES})

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and Usuario.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con ese correo.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit: bool = True, *args, **kwargs):
        """
        Guarda Usuario y luego crea Operador.
        Acepta empresa como keyword argument (empresa=...).
        """
        empresa: Optional[Empresa] = kwargs.pop("empresa", None)
        if empresa is None:
            raise ValueError("Se requiere la instancia 'empresa' al guardar el operador.")

        usuario: Usuario = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            usuario.set_password(password)

        try:
            usuario.rol = Rol.objects.get(pk=3)
        except Rol.DoesNotExist:
            pass

        with transaction.atomic():
            if commit:
                usuario.save()
                Operador.objects.create(
                    usuario=usuario,
                    cargo=self.cleaned_data.get("cargo", ""),
                    empresa=empresa
                )
            else:
                return usuario

        return usuario