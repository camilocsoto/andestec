from django.db import models
from django.utils import timezone
from accounts.models import Empresa, Usuario


class TipoSensor(models.Model):
    nombre = models.CharField(max_length=45, verbose_name="nombre del tipo de sensor")
    descripcion = models.CharField(max_length=45, null=True, blank=True, verbose_name="descripción del tipo de sensor")

    class Meta:
        db_table = 'tipoSensor'

    def __str__(self):
        return f"{self.nombre}-{self.descripcion}"


class Sensor(models.Model):
    nombre = models.CharField(max_length=45, null=True, blank=True, verbose_name="nombre del sensor")
    estado = models.BinaryField(null=True, blank=True, verbose_name="estado del sensor")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True, verbose_name="empresa del sensor")
    tipoSensor = models.ForeignKey(TipoSensor, on_delete=models.PROTECT, verbose_name="tipo del sensor")

    class Meta:
        db_table = 'Sensor'

    def __str__(self):
        return f"{self.nombre} está ({self.estado})"

class ServerCredentials(models.Model):
    nombre = models.CharField(max_length=45, null=True, blank=True, verbose_name="nombre")
    user = models.CharField(max_length=45, null=True, blank=True, verbose_name="usuario")
    password = models.CharField(max_length=45, null=True, blank=True, verbose_name="contraseña")
    authorization = models.CharField(max_length=100, null=True, blank=True, verbose_name="autorización")
    descripcion = models.CharField(max_length=100, null=True, blank=True, verbose_name="descripcion")
    server_userId = models.CharField(max_length=10, null=True, blank=True, verbose_name="id de user en el servidor")
    server_clientId = models.CharField(max_length=45, null=True, blank=True, verbose_name="id unico de cliente en el servidor")
    server_access_token = models.CharField(max_length=85, null=True, blank=True, verbose_name="token de acceso")
    token_updated = models.DateTimeField(null=True, blank=True, verbose_name="ultima actualización del token")

    class Meta:
        db_table = 'server_credentials'

    def __str__(self):
        return f"Credentials con acceso al servidor de {self.nombre}"
    
class GasRestante(models.Model):
    # PK = Sensor_idSensor (one-to-one relationship; PK is sensor)
    Sensor_idSensor = models.OneToOneField(
        Sensor,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name="Sensor_idSensor"
    )
    localizacion = models.CharField(max_length=45, null=True, blank=True, verbose_name="localización del sensor")
    bateria = models.CharField(max_length=45, null=True, blank=True, verbose_name="batería restante")
    toleranciaMins = models.IntegerField(null=True, blank=True, verbose_name="tolerancia de tiempo en mins")
    server_deviceNo = models.CharField(max_length=85, null=True, blank=True, verbose_name="server deviceNo")
    server_credentials = models.ForeignKey(ServerCredentials, on_delete=models.CASCADE, verbose_name="credenciales del servidor")

    class Meta:
        db_table = 'GasRestante'
    
    def __str__(self):
        return f"{self.Sensor_idSensor.nombre} - {self.server_deviceNo}"
        
class ComposicionGas(models.Model):
    nombre = models.CharField(max_length=45, null=True, blank=True, verbose_name="nombre")
    descripcion = models.CharField(max_length=100, null=True, blank=True, verbose_name="descripcion")
    masa_molar = models.FloatField(null=True, blank=True, verbose_name="masa molar")
    y_entropia = models.FloatField(null=True, blank=True, verbose_name="y entropia")
    z_factor = models.FloatField(null=True, blank=True, verbose_name="z factor")
    densidad = models.FloatField(null=True, blank=True, verbose_name="densidad")

    class Meta:
        db_table = 'ComposicionGas'

    def __str__(self):
        return f'el gas{self.nombre} tiene {self.descripcion}'

        

class CaracteristicasCilindro(models.Model):
    nombre = models.CharField(max_length=45, null=True, blank=True, verbose_name="nombre")
    volumen_interno_m3 = models.FloatField(null=True, blank=True, verbose_name="volumen interno (m3)")
    masa_cil_vacio_kg = models.FloatField(null=True, blank=True, verbose_name="masa cilindro al vacío (Kg)")
    masa_cil_lleno_kg = models.FloatField(null=True, blank=True, verbose_name="masa cilindro lleno (Kg")
    masa_gas_restant_kg = models.FloatField(null=True, blank=True, verbose_name="cant. gas restante (Kg")    
    coef_descarga_cd = models.FloatField(null=True, blank=True, verbose_name="coeficiente de descarga (cd)")
    diametro_orificio_m = models.FloatField(null=True, blank=True, verbose_name="diametro de orificio (m")
    notas = models.CharField(max_length=45, null=True, blank=True, verbose_name="notas")
    ComposicionGas = models.ForeignKey(ComposicionGas, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Composición del gas")
    GasRestante = models.ForeignKey(GasRestante, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="sensor de gas restante")

    class Meta:
        db_table = 'CaracteristicasCilindro'

    def __str__(self):
        return f"cilindro {self.nombre} no. {self.pk}"



class ResultsGasRestante(models.Model):
    ESTATUS_FASE = (
        (None, 'Ninguno'),
        ('choked', 'Ahogado'),
        ('no_choked', 'No ahogado'),
    )
    timestamp = models.DateTimeField(null=True, blank=True, verbose_name="última actualización", default=timezone.now)
    presion_gauge_pa = models.FloatField(null=True, blank=True, verbose_name="presión manómetro (Pa)")
    presion_abs_pa = models.FloatField(null=True, blank=True, verbose_name="presión abs. (Pa)")
    temperature_k = models.FloatField(null=True, blank=True, verbose_name="temperatura (k)")
    estado_fase = models.CharField(choices = ESTATUS_FASE, default = 'None', max_length=20, null=True, blank=True, verbose_name="estado de fase del gas")
    caudal_masa_kg_s = models.FloatField(null=True, blank=True, verbose_name="caudal de masa (Kg/s)")
    masa_remov_kg = models.FloatField(null=True, blank=True, verbose_name="masa de gas removida (Kg)")
    masa_restante_kg = models.FloatField(null=True, blank=True, verbose_name="masa de gas restante (Kg)")
    moles_restantes_kg = models.FloatField(null=True, blank=True, verbose_name="cant. de moles restantes (Kg)")
    metodo_calculo = models.CharField(max_length=45, null=True, blank=True, verbose_name="método del cálculo")
    masa_balanza_kg = models.FloatField(null=True, blank=True, verbose_name="nuevo peso de la balanza (Kg)")
    porc_masa_gas_restant = models.FloatField(null=True, blank=True, verbose_name="porc. masa gas restante (%)")
    porc_masa_gas_extracted = models.FloatField(null=True, blank=True, verbose_name="porc. masa gas utilizada (%)")
    valido = models.SmallIntegerField(null=True, blank=True, verbose_name="cálculos válidos")
    caracteristicas_cilindro = models.ForeignKey(CaracteristicasCilindro, on_delete=models.CASCADE, verbose_name="Cilindro a monitorear")
    class Meta:
        db_table = 'ResultsGasRestante'

    def __str__(self):
        return f"({self.timestamp})"


class Alarma(models.Model):
    nombreAlarma = models.CharField(max_length=45, null=True, blank=True, verbose_name="nombre alarma")
    fecha = models.DateTimeField(null=True, blank=True, verbose_name="fecha")
    descripcion = models.TextField(null=True, blank=True, verbose_name="descripción")
    estado = models.BooleanField(null=True, blank=True, verbose_name="estado")
    Sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, verbose_name="sensor")

    class Meta:
        db_table = 'alarma'

    def __str__(self):
        return f"Alarma {self.nombreAlarma} - {self.estado}"


class TipoPeticion(models.Model):
    nombre = models.CharField(max_length=45, null=True, blank=True, verbose_name="nombre")

    class Meta:
        db_table = 'TipoPeticion'

    def __str__(self):
        return self.nombre or f"TipoPeticion {self.pk}"

class TcketSoporte(models.Model):
    IMPORTANCIA = (
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta')
    )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="mensaje de la empresa")
    TipoPeticion = models.ForeignKey(TipoPeticion, on_delete=models.PROTECT, verbose_name="Tipo de peticion")
    asunto = models.CharField(max_length=100, null=True, blank=True, verbose_name="asunto")
    NivelImportancia = models.CharField(choices = IMPORTANCIA, default='Baja', verbose_name="Nivel de importancia")
    estado = models.BinaryField(null=True, blank=True, verbose_name="estado")
    descripcion = models.TextField(null=True, blank=True, verbose_name="descripción")
    fecha_creacion = models.DateTimeField(null=True, blank=True, verbose_name="fecha de creacion")
    fecha_actualizacion = models.DateTimeField(null=True, blank=True, verbose_name="fecha de actualizacion")
    archivos_comprimidos = models.BinaryField(null=True, blank=True, verbose_name="archivos comprimidos")

    class Meta:
        db_table = 'TcketSoporte'

    def __str__(self):
        return f"TcketSoporte {self.pk} - {self.asunto}"
    
class Mensaje(models.Model):
    mensajes = models.TextField(null=True, blank=True, verbose_name="mensaje")
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="hora y fecha del comentario")
    Usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="usuario")
    TcketSoporte = models.ForeignKey(TcketSoporte, on_delete=models.CASCADE, verbose_name="ticket soporte")

    class Meta:
        db_table = 'mensajes'

    def __str__(self):
        return f"Mensaje de {self.Usuario} dice {self.mensajes}"
