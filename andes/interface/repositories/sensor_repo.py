from ..models import Sensor, GasRestante, TipoSensor
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

class SensorTPRepository:
    
    def get_all(self):
        return Sensor.objects.all()
    
    def get_sensor_with_related(self, pk: int) -> Sensor:
        return Sensor.objects.select_related("empresa", "tipoSensor").get(pk=pk)

    @transaction.atomic
    def create_gas_tp_sensor( self, *, nombre: str | None, estado_bytes: bytes | None, empresa, tipo_id: int, localizacion: str | None, bateria: str | None, server_deviceNo: str | None, server_credentials) -> Sensor:
        """Crea Sensor + GasRestante para tipoSensor"""
        tipo = TipoSensor.objects.get(pk=tipo_id)
        sensor = Sensor.objects.create(
            nombre=nombre,
            estado=estado_bytes,
            empresa=empresa,
            tipoSensor=tipo,
        )
        GasRestante.objects.create(
            Sensor_idSensor=sensor,
            localizacion=localizacion,
            bateria=bateria,
            server_deviceNo=server_deviceNo,
            server_credentials=server_credentials,
        )
        return sensor
    
    @transaction.atomic
    def update_gas_tpsensor( self, *, sensor_id: int, nombre, estado_bytes, empresa, localizacion, bateria, server_deviceNo, server_credentials) -> Sensor:
        sensor = Sensor.objects.select_for_update().select_related("tipoSensor").get(pk=sensor_id)
        # actualizar Sensor
        sensor.nombre = nombre
        sensor.estado = estado_bytes
        sensor.empresa = empresa
        sensor.save(update_fields=["nombre", "estado", "empresa"])

        # actualizar GasRestante (pk = sensor)
        gas = GasRestante.objects.select_for_update().get(Sensor_idSensor_id=sensor_id)
        gas.localizacion = localizacion
        gas.bateria = bateria
        gas.server_deviceNo = server_deviceNo
        gas.server_credentials = server_credentials
        gas.save(update_fields=["localizacion", "bateria", "server_deviceNo", "server_credentials"])
        return sensor
    
    @transaction.atomic
    def delete_sensor(self, sensor_id: int) -> int:
        """
        Borra el sensor (y en cascada GasRestante). Devuelve cantidad eliminada (1 si ok).
        """
        try:
            obj = Sensor.objects.select_for_update().get(pk=sensor_id)
        except ObjectDoesNotExist:
            return 0
        obj.delete()  # GasRestante cae por cascade
        return 1