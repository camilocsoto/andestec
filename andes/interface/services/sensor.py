from ..repositories.sensor_repo import SensorTPRepository
from ..strategies.sensor import SensorStrategy, SensorDetailStrategy, DetailSensor, SelectpDataStrategy
from ..models import Sensor, GasRestante, TipoSensor
from typing import cast, Dict, Any

class SensorService:
    
    def __init__(self):
        self.repo = SensorTPRepository() # just to list all sensors in admin menu
        self.create_strategy = SensorStrategy()
        self.detail_strategy = SensorDetailStrategy()

    def get_all_sensors(self): 
        # list all sensors to the list view
        return self.repo.get_all()
    
    def create_tpsensor(self, *, tipo_id: int, data: dict) -> Sensor:
        """
        data viene de form.cleaned_data. Strategy elige form/repo/plantilla.
        """
        cfg = self.create_strategy.resolve(tipo_id)
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

        cfg = self.create_strategy.resolve_update(tipo_id)
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


    def build_detail(self, sensor_id: int) -> DetailSensor:
        """
        Devuelve un payload {"template_name": str, "context": dict}
        armado por la strategy, a partir del sensor y su tipo.
        """
        sensor = Sensor.objects.select_related("tipoSensor").get(pk=sensor_id)
        tipo_id = sensor.tipoSensor.pk
        return self.detail_strategy.resolve(sensor_id=sensor_id, tipo_id=tipo_id)
    
    def build_gas_dashboard(self, *, sensor_id: int, strategy: str = "latest_5_reg", **extra) -> Dict[str, Any]:
        """ Orquesta la construcción del contexto del dashboard de gas. """
        
        # valida existencia básica del sensor, si no está 404
        Sensor.objects.only("id").get(pk=sensor_id)

        selector = SelectpDataStrategy()
        data = selector.run(sensor_id=sensor_id, strategy=strategy, extra=extra or None)

        # Puedes enriquecer el contexto aquí si quieres (títulos, flags, etc.)
        return {
            "sensor_id": sensor_id,
            "strategy": strategy,
            "data": data,   # <- datos del sensor
        }

    
