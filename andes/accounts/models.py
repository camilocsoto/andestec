from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class TipoDocumento(models.Model):
    nombreDoc = models.CharField(max_length=45, verbose_name="nombreDoc")

    class Meta:
        db_table = 'TipoDocumento'

    def __str__(self):
        return self.nombreDoc or f"{self.pk}-{self.nombreDoc}"


class Rol(models.Model):
    nombreRol = models.CharField(max_length=45, verbose_name="nombreRol")

    class Meta:
        db_table = 'rol'

    def __str__(self):
        return self.nombreRol or f"{self.pk}-{self.nombreRol}"


class Usuario(AbstractUser):
    # (no repito username/password/first_name/last_name salvo email para hacerlo unique)
    email = models.EmailField(unique=True, verbose_name="mail")
    tipo_documento = models.ForeignKey(
        TipoDocumento, on_delete=models.PROTECT,
        null=True, blank=True, verbose_name="TipoDocumento"
    )
    numDocumento = models.CharField(max_length=45, null=True, blank=True, verbose_name="numDocumento")
    image = models.BinaryField(null=True, blank=True, verbose_name="image")
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True, blank=True, verbose_name="rol")
    # si el SQL tiene un campo "estado" tinyint(1) lo mapeo a BooleanField:
    estado = models.BooleanField(default=True, verbose_name="estado")

    class Meta:
        db_table = 'Usuario'

    def save(self, *args, **kwargs):
        # asegurar que username sea por defecto igual al email (si hay email)
        if self.email:
            # Solo sobreescribo username si está vacío o diferente
            if not self.username or self.username != self.email:
                self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name() or self.username} <{self.email}>"


class Empresa(models.Model):
    # relación fuerte: la PK de Empresa es el id del Usuario (igual que en tu SQL)
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE,
        primary_key=True, verbose_name="Usuario"
    )
    cantidadOperarios = models.CharField(max_length=45, null=True, blank=True, verbose_name="cantidadOperarios")
    direccion = models.CharField(max_length=45, null=True, blank=True, verbose_name="direccion")

    class Meta:
        db_table = 'empresa'

    def __str__(self):
        return f"Empresa de {self.usuario}"


class Operador(models.Model):
    # relación fuerte: PK = Usuario.id y además referencia a empresa
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE,
        primary_key=True, verbose_name="Usuario"
    )
    area = models.CharField(max_length=45, null=True, blank=True, verbose_name="area")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="empresa")

    class Meta:
        db_table = 'operador'

    def __str__(self):
        return f"Operador {self.usuario}"
