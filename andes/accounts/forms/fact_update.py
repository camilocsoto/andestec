from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from accounts.models import Usuario, Empresa, TipoDocumento

INPUT_CLASSES = (
    "block w-full rounded-md border-gray-300 shadow-sm sm:text-sm "
    "focus:ring-indigo-500 focus:border-indigo-500 "
    "dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
)

class EmpresaUpdateForm(forms.ModelForm):
    # Campos de Usuario
    first_name = forms.CharField(label="Nombre", max_length=150, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
    last_name = forms.CharField(label="Apellido", max_length=150, required=False, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
    tipo_documento = forms.ModelChoiceField(
        queryset=TipoDocumento.objects.all(),
        label="Tipo de documento",
        required=False,
        widget=forms.Select(attrs={"class": "block w-full rounded-md border-gray-300 sm:text-sm dark:bg-gray-700 dark:border-gray-600"})
    )
    numDocumento = forms.CharField(label="Documento", max_length=45, required=False, widget=forms.TextInput(attrs={"class": INPUT_CLASSES}))
    email = forms.EmailField(label="Correo", widget=forms.EmailInput(attrs={"class": INPUT_CLASSES}))
    estado = forms.BooleanField(label="Activo", required=False)

    # Campos de Empresa (ModelForm Meta)
    class Meta:
        model = Empresa
        fields = ["direccion", "cantidadOperarios"]
        widgets = {
            "direccion": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "cantidadOperarios": forms.TextInput(attrs={"class": INPUT_CLASSES})
        }

    def __init__(self, *args, **kwargs):
        """
        Espera pasar 'usuario' opcional (instancia Usuario) o 'instance' Empresa (cuando UpdateView la instancia pasa).
        Si se pasa 'usuario' o 'instance' rellena los initial apropiados.
        """
        usuario = kwargs.pop("usuario", None)
        super().__init__(*args, **kwargs)

        # Si la form fue instanciada con instance (Empresa), obtener su usuario
        if usuario is None and self.instance and getattr(self.instance, "usuario", None):
            usuario = self.instance.usuario

        if usuario:
            self.fields["first_name"].initial = usuario.first_name
            self.fields["last_name"].initial = usuario.last_name
            self.fields["tipo_documento"].initial = usuario.tipo_documento
            self.fields["numDocumento"].initial = usuario.numDocumento
            self.fields["email"].initial = usuario.email
            self.fields["estado"].initial = usuario.estado

    def clean_email(self):
        email = self.cleaned_data.get("email")
        # si existe otro usuario con ese email, bloquear
        if email:
            qs = Usuario.objects.filter(email=email)
            # si estamos en update, excluir al usuario actual
            usuario_actual = None
            if self.instance and getattr(self.instance, "usuario", None):
                usuario_actual = self.instance.usuario
            if usuario_actual:
                qs = qs.exclude(pk=usuario_actual.pk)
            if qs.exists():
                raise ValidationError("Ya existe un usuario con ese correo.")
        return email

    def save(self, commit=True):
        """
        Guarda Usuario y Empresa en una transacción.
        """
        # Primero guardar la empresa parcialmente
        empresa = super().save(commit=False)

        # obtener/crear usuario relacionado
        usuario = None
        if self.instance and getattr(self.instance, "usuario", None):
            usuario = self.instance.usuario
        # si no hay usuario (caso raro), no intentamos crear uno aquí
        if usuario is None:
            raise ValidationError("No se encontró el usuario asociado a la empresa.")

        # actualizar campos del usuario
        usuario.first_name = self.cleaned_data.get("first_name", usuario.first_name)
        usuario.last_name = self.cleaned_data.get("last_name", usuario.last_name)
        usuario.tipo_documento = self.cleaned_data.get("tipo_documento", usuario.tipo_documento)
        usuario.numDocumento = self.cleaned_data.get("numDocumento", usuario.numDocumento)
        usuario.email = self.cleaned_data.get("email", usuario.email)
        usuario.estado = self.cleaned_data.get("estado", usuario.estado)

        # Guardado atómico
        with transaction.atomic():
            usuario.save()
            empresa.usuario = usuario
            if commit:
                empresa.save()

        return empresa
