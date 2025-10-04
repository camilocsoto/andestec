from ..repositories.sensor_repo import SensorTPRepository
from ..strategies.sensor import SensorStrategy
from ..models import Sensor, GasRestante, TipoSensor


class SensorService:
    def __init__(self):
        self.repo = SensorTPRepository() # just to list all sensors in admin menu
        self.strategy = SensorStrategy()

    def get_all_sensors(self): 
        # list all sensors to the list view
        return self.repo.get_all()
    
    def create_tpsensor(self, *, tipo_id: int, data: dict) -> Sensor:
        """
        data viene de form.cleaned_data. Strategy elige form/repo/plantilla.
        """
        cfg = self.strategy.resolve(tipo_id)
        repo = cfg["repo"]

        # Mapea booleano -> BinaryField
        estado = data.get("estado")
        estado_bytes = None if estado is None else (b"\x01" if estado else b"\x00")

        sensor = repo.create_gas_tp_sensor(
            nombre=data.get("nombre"),
            estado_bytes=estado_bytes,
            empresa=data.get("empresa"),
            tipo_id=tipo_id,
            localizacion=data.get("localizacion"),
            bateria=data.get("bateria"),
            server_deviceNo=data.get("server_deviceNo"),
            server_credentials=data.get("server_credentials"),
        )
        return sensor
    # update
    def get_update_initial(self, *, sensor_id: int) -> dict:
        sensor = self.repo.get_sensor_with_related(sensor_id)
        try:
            gas = GasRestante.objects.get(Sensor_idSensor_id=sensor_id)
        except GasRestante.DoesNotExist:
            gas = None

        return {
            "nombre": sensor.nombre,
            "estado": (sensor.estado == b"\x01") if sensor.estado is not None else None,
            "empresa": sensor.empresa.usuario.pk if sensor.empresa and sensor.empresa.usuario else None,
            "localizacion": gas.localizacion if gas else "",
            "bateria": gas.bateria if gas else "",
            "server_deviceNo": gas.server_deviceNo if gas else "",
            "server_credentials": gas.server_credentials.pk if gas else None,
            # si en el form aparece tipoSensor, lo ignoraremos en update()
        }

    def update(self, *, sensor_id: int, data: dict) -> Sensor:
        sensor = self.repo.get_sensor_with_related(sensor_id)
        tipo_id = sensor.tipoSensor.pk  # para resolver strategy

        # si form trae 'tipoSensor', lo ignoramos:
        data = {k: v for k, v in data.items() if k != "tipoSensor"}

        cfg = self.strategy.resolve_update(tipo_id)
        repo = cfg["repo"]

        estado = data.get("estado")
        estado_bytes = None if estado is None else (b"\x01" if estado else b"\x00")

        return repo.update_gas_tpsensor(
            sensor_id=sensor_id,
            nombre=data.get("nombre"),
            estado_bytes=estado_bytes,
            empresa=data.get("empresa"),
            localizacion=data.get("localizacion"),
            bateria=data.get("bateria"),
            server_deviceNo=data.get("server_deviceNo"),
            server_credentials=data.get("server_credentials"),
        )
        
    def delete(self, *, sensor_id: int) -> bool:
        deleted = self.repo.delete_sensor(sensor_id)
        return deleted == 1

