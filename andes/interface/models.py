from django.db import models
from django.utils import timezone
from accounts.models import Empresa


class TipoSensor(models.Model):
    nombre = models.CharField(max_length=45, verbose_name="nombreTipoSensor")

    class Meta:
        db_table = 'tipoSensor'

    def __str__(self):
        return self.nombre or f"{self.pk}-{self.nombre}"


class Sensor(models.Model):
    nombre = models.CharField(max_length=45, null=True, blank=True, verbose_name="nombre")
    imei = models.CharField(max_length=45, null=True, blank=True, verbose_name="imei")
    numSerial = models.CharField(max_length=45, null=True, blank=True, verbose_name="numSerial")
    estado = models.BinaryField(null=True, blank=True, verbose_name="estado")
    localizacion = models.CharField(max_length=45, null=True, blank=True, verbose_name="localizacion")
    bateria = models.SmallIntegerField(null=True, blank=True, verbose_name="bateria")
    senal = models.CharField(max_length=45, null=True, blank=True, verbose_name="señal")
    ultimaActualizacion = models.DateTimeField(null=True, blank=True, verbose_name="ultimaActualizacion")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True, verbose_name="empresa")
    tipoSensor = models.ForeignKey(TipoSensor, on_delete=models.PROTECT, verbose_name="tipoSensor")

    class Meta:
        db_table = 'Sensor'

    def __str__(self):
        return f"{self.nombre or self.numSerial} ({self.imei})"


class CaracteristicasMedidor(models.Model):
    TipoMedidor = models.CharField(max_length=45, null=True, blank=True, verbose_name="TipoMedidor")
    CapacidadMaximaKg = models.SmallIntegerField(null=True, blank=True, verbose_name="CapacidadMaximaKg")
    PesoActualCilindroKg = models.SmallIntegerField(null=True, blank=True, verbose_name="PesoActualCilindroKg")
    PresionMaximaPSI = models.SmallIntegerField(null=True, blank=True, verbose_name="PresionMaximaPSI")
    CaracteristicasMedidorcol = models.CharField(max_length=45, null=True, blank=True, verbose_name="CaracterísticasMedidorcol")
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, verbose_name="Sensor")

    class Meta:
        db_table = 'CaracterísticasMedidor'

    def __str__(self):
        return f"CaracterísticasMedidor {self.pk} para {self.sensor}"


class Variables(models.Model):
    fechaActualizacion = models.DateTimeField(null=True, blank=True, verbose_name="fechaActualizacion")
    presion = models.SmallIntegerField(null=True, blank=True, verbose_name="presion")
    temperatura = models.SmallIntegerField(null=True, blank=True, verbose_name="temperatura")
    densidad = models.SmallIntegerField(null=True, blank=True, verbose_name="densidad")
    cantidad_actual_gas = models.SmallIntegerField(null=True, blank=True, verbose_name="cantidad_actual_gas")
    cantidad_actual_porcentaje = models.SmallIntegerField(null=True, blank=True, verbose_name="cantidad_actual_porcentaje")
    caudal = models.SmallIntegerField(null=True, blank=True, verbose_name="caudal")
    caracteristicas_medidor = models.ForeignKey(CaracteristicasMedidor, on_delete=models.CASCADE, verbose_name="CaracterísticasMedidor")

    class Meta:
        db_table = 'Variables'

    def __str__(self):
        return f"Variables {self.pk} ({self.fechaActualizacion})"


class TipoPeticion(models.Model):
    nombre = models.CharField(max_length=45, null=True, blank=True, verbose_name="nombre")

    class Meta:
        db_table = 'TipoPeticion'

    def __str__(self):
        return self.nombre or f"TipoPeticion {self.pk}"


class NivelImportancia(models.Model):
    Nombre = models.CharField(max_length=45, null=True, blank=True, verbose_name="Nombre")

    class Meta:
        db_table = 'NivelImportancia'

    def __str__(self):
        return self.Nombre or f"NivelImportancia {self.pk}"


class TcketSoporte(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="empresa")
    TipoPeticion = models.ForeignKey(TipoPeticion, on_delete=models.PROTECT, verbose_name="TipoPeticion")
    asunto = models.CharField(max_length=100, null=True, blank=True, verbose_name="asunto")
    NivelImportancia = models.ForeignKey(NivelImportancia, on_delete=models.PROTECT, verbose_name="NivelImportancia")
    estado = models.BinaryField(null=True, blank=True, verbose_name="estado")
    descripcion = models.TextField(null=True, blank=True, verbose_name="descripcion")
    fecha_creacion = models.DateTimeField(null=True, blank=True, verbose_name="fecha_creacion")
    fecha_actualizacion = models.DateTimeField(null=True, blank=True, verbose_name="fecha_actualizacion")
    archivos_comprimidos = models.BinaryField(null=True, blank=True, verbose_name="archivos_comprimidos")

    class Meta:
        db_table = 'TcketSoporte'

    def __str__(self):
        return f"TcketSoporte {self.pk} - {self.asunto}"


class Notificacion(models.Model):
    nombre_notificacion = models.CharField(max_length=45, null=True, blank=True, verbose_name="nombre_notificacion")
    estado = models.BooleanField(null=True, blank=True, verbose_name="estado")
    descripcion = models.TextField(null=True, blank=True, verbose_name="descripcion")

    class Meta:
        db_table = 'notificacion'

    def __str__(self):
        return self.nombre_notificacion or f"Notificacion {self.pk}"


class Alarma(models.Model):
    nombreAlarma = models.CharField(max_length=45, null=True, blank=True, verbose_name="nombreAlarma")
    fecha = models.DateTimeField(null=True, blank=True, verbose_name="fecha")
    descripcion = models.TextField(null=True, blank=True, verbose_name="descripcion")
    estado = models.BooleanField(null=True, blank=True, verbose_name="estado")
    Sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, verbose_name="Sensor")
    notificacion = models.ForeignKey(Notificacion, on_delete=models.CASCADE, verbose_name="notificacion")

    class Meta:
        db_table = 'alarma'

    def __str__(self):
        return f"Alarma {self.nombreAlarma} ({self.pk})"