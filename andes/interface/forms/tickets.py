from typing import Optional
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
import os
from interface.models import TcketSoporte, TipoPeticion
from accounts.models import Empresa

MAX_UPLOAD_SIZE = 1 * 1024 * 1024  # 1 MB
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.pdf', '.xlsx'}

# clases tailwind (opcional)
INPUT_CLASSES = (
    "block w-full rounded-md border-gray-300 shadow-sm sm:text-sm "
    "focus:ring-indigo-500 focus:border-indigo-500 "
    "dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
)


def _validate_file_size(f):
    if f.size > MAX_UPLOAD_SIZE:
        raise ValidationError(f"El archivo excede el tamaño máximo permitido ({MAX_UPLOAD_SIZE // 1024} KB).")


def _validate_file_extension(f):
    _, ext = os.path.splitext(f.name.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"Extensión no permitida. Solo se aceptan: {', '.join(sorted(ALLOWED_EXTENSIONS))}.")


# --- ticket gests ---

class TicketSoporteForm(forms.ModelForm):
    """
    Form para crear/editar TcketSoporte.
    - Usa campo 'archivo' para subir un único archivo (png/jpg/pdf/xlsx).
    - Guarda bytes en `archivos_comprimidos`.
    - La empresa se pasa al guardar: form.save(empresa=empresa)
    """


    # TipoPeticion: listado desde la tabla TipoPeticion
    TipoPeticion = forms.ModelChoiceField(
        queryset=TipoPeticion.objects.all(),
        label="Tipo de petición",
        required=True,
        widget=forms.Select(attrs={"class": INPUT_CLASSES})
    )

    # Campo para subir un único archivo
    archivo = forms.FileField(
        label="Archivo adjunto (opcional)",
        required=False,
        validators=[_validate_file_extension, _validate_file_size],
        help_text="Max 1MB. Formatos: png, jpg, jpeg, pdf, xlsx."    
    )
    # Representamos estado (BinaryField en el modelo) como un checkbox booleano en el form
    estado_bool = forms.BooleanField(label="Completado", required=False)

    class Meta:
        model = TcketSoporte
        # NivelImportancia está en el modelo con choices, lo incluimos para que el select salga automático
        fields = [
            "TipoPeticion",
            "asunto",
            "NivelImportancia",
            "descripcion",
        ]
        widgets = {
            "asunto": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "NivelImportancia": forms.Select(attrs={"class": INPUT_CLASSES}),
            "descripcion": forms.Textarea(attrs={"class": INPUT_CLASSES, "rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        """ Si se instancia con una instancia del modelo (update), rellenamos estado_bool desde el campo binary."""
        super().__init__(*args, **kwargs)

        # inicializar estado_bool a partir de self.instance.estado si existe
        if self.instance and getattr(self.instance, "estado", None) is not None:
            # interpretamos cualquier contenido distinto de b'\x00' como True
            try:
                self.fields["estado_bool"].initial = bool(self.instance.estado and self.instance.estado != b'\x00')
            except Exception:
                self.fields["estado_bool"].initial = False
        else:
            self.fields["estado_bool"].initial = False

    def clean(self):
        cleaned = super().clean()
        # validaciones extra si se requieren (por ejemplo asunto obligatorio en ciertos tipos)
        return cleaned

    def save(self, commit: bool = True, empresa: Optional[Empresa] = None) -> TcketSoporte:
        """
        Guarda el ticket. Requiere empresa.
        Convierte el campo estado_bool a bytes y guarda archivo en archivos_comprimidos si existe.
        Actualiza fechas de creación/actualización.
        """
        if empresa is None:
            raise ValueError("Se requiere la instancia 'empresa' al guardar el ticket.")

        ticket: TcketSoporte = super().save(commit=False)

        ticket.empresa = empresa

        now = timezone.now()
        if not ticket.fecha_creacion:
            ticket.fecha_creacion = now
        ticket.fecha_actualizacion = now

        estado_bool = self.cleaned_data.get("estado_bool")
        if estado_bool is None:
            ticket.estado = None
        else:
            ticket.estado = b'\x01' if estado_bool else b'\x00'

        # archivo (si se subió)
        uploaded_file = self.cleaned_data.get("archivo")
        if uploaded_file:
            try:
                # En algunos entornos uploaded_file.read() puede agotar el stream,
                # pero aquí lo hacemos explícito y registramos tamaño.
                file_bytes = uploaded_file.read()
                ticket.archivos_comprimidos = file_bytes
                print(f"DEBUG: archivo subido: name={uploaded_file.name}, size={len(file_bytes)} bytes")
            except Exception as e:
                # si hay problema leyendo bytes, lanzar excepción para que la vista la capture
                print("DEBUG: error leyendo archivo subido:", e)
                raise

        # Forzamos guardar y retornamos la instancia guardada
        if commit:
            ticket.save()
            # refrescar desde BD por si hay triggers o valores por defecto
            ticket.refresh_from_db()
        return ticket