from ..repositories.sensor_repo import SensorTPRepository
from ..strategies.sensor import SensorStrategy, SensorDetailStrategy, DetailSensor, SelectpDataStrategy, ConnectionEvalStrategy
from ..models import Sensor, GasRestante, TipoSensor
from typing import cast, Dict, Any
from django.db.models import QuerySet

class SensorService:
    """
    class used for orchestration of sensor operations such as:
    - 
    """
    def __init__(self):
        self.repo = SensorTPRepository() # just to list all sensors in admin menu
        self.strategy = SensorStrategy()
        self.detail_strategy = SensorDetailStrategy()
        self.conn_strategy = ConnectionEvalStrategy()

    def get_all_sensors(self): 
        # list all sensors to the admins view
        return self.repo.get_all()
    
    def create_sensor(self, *, tipo_id: int, data: dict) -> Sensor:
        """
        data viene de form.cleaned_data. Strategy elige form/repo/plantilla.
        """
        cfg = self.strategy.resolve(tipo_id)
        repo = cfg["repo"]
        sensor = repo(tipo_id=tipo_id, data=data)
        return sensor
    
    # update
    def _resolve_cfg_by_sensor(self, sensor_id: int):
        sensor = Sensor.objects.select_related("tipoSensor").get(pk=sensor_id)
        tipo_id = sensor.tipoSensor.pk
        cfg = self.strategy.resolve_update(tipo_id)
        return cfg

    # --- UPDATE: initial ---
    def get_update_initial(self, *, sensor_id: int) -> dict:
        cfg = self._resolve_cfg_by_sensor(sensor_id)
        repo = cfg["repo"]
        return repo.get_update_initial_data(sensor_id=sensor_id)

    # --- UPDATE: submit ---
    def update(self, *, sensor_id: int, data: dict) -> Sensor:
        cfg = self._resolve_cfg_by_sensor(sensor_id)
        repo = cfg["repo"]
        # delega todo al repo
        return repo.update_from_form(sensor_id=sensor_id, data=data)
        
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
        
    def eval_conn(self) -> None:
        """
        Itera todos los sensores y evalúa su estado de conexión.
        """
        qs: QuerySet[Sensor] = Sensor.objects.select_related("tipoSensor").all()
        for sensor in qs:
            tipo_id = sensor.tipoSensor.pk
            evaluator = self.conn_strategy.resolve_eval_callable(tipo_id=tipo_id)
            # cada evaluador recibe el objeto sensor
            evaluator(sensor)

    
