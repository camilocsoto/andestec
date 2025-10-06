from ..models import Sensor, GasRestante, TipoSensor, CaracteristicasCilindro, ComposicionGas, ResultsGasRestante
from typing import Tuple, Dict, Any
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import OuterRef, Subquery, QuerySet
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
    
class SensorTPDetailRepository:
    def get_sensor_base(self, sensor_id: int) -> Sensor:
        return (Sensor.objects
                .select_related("empresa__usuario", "tipoSensor")
                .get(pk=sensor_id))

    def get_gasrestante_for_sensor(self, sensor_id: int) -> GasRestante | None:
        try:
            return (GasRestante.objects
                    .select_related("server_credentials", "Sensor_idSensor")
                    .get(Sensor_idSensor_id=sensor_id))
        except GasRestante.DoesNotExist:
            return None

    def get_cylinders_with_latest_result(self, gas: GasRestante) -> Tuple[QuerySet, Dict[int, ResultsGasRestante]]:
        """
        Devuelve (cilindros_qs, latest_results_map)
        - cilindros_qs: queryset de CaracteristicasCilindro anotado con latest_result_id
        - latest_results_map: dict {latest_result_id: ResultsGasRestante}
        """
        if gas is None:
            return CaracteristicasCilindro.objects.none(), {}

        latest_result_subq = (
            ResultsGasRestante.objects
            .filter(CaracterísticasCilindro=OuterRef('pk'))
            .order_by('-timestamp')
            .values('id')[:1]
        )

        cilindros_qs = (
            CaracteristicasCilindro.objects
            .select_related('ComposicionGas', 'GasRestante')
            .filter(GasRestante=gas)
            .annotate(latest_result_id=Subquery(latest_result_subq))
        )

        # Extraer los ids anotados sin acceder a atributos dinámicos en instancias
        ids_qs = cilindros_qs.values_list('latest_result_id', flat=True)
        # materializar y filtrar None/0/'' (lo que sea no válido)
        ids = [int(i) for i in ids_qs if i]

        latest_results = ResultsGasRestante.objects.in_bulk(ids) if ids else {}

        return cilindros_qs, latest_results