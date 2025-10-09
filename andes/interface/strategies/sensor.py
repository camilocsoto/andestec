from typing import TypedDict, Type, Optional, List, Dict, Any, cast, Callable
from django import forms
from django.db.models import QuerySet
from interface.forms.tp_sensor import SensorTPForm
from ..repositories.sensor_repo import SensorTPRepository, SensorTPDetailRepository, GasDashboardRepository, SensorTPEvalConnRepository
from ..models import Sensor, GasRestante, TipoSensor, CaracteristicasCilindro, ComposicionGas, ResultsGasRestante

class SensorConfig(TypedDict):
    form_class: Type[forms.Form]
    template_name: str
    repo: Any # instancia de repo con create_from_form / get_update_initial_data / update_from_form
    
class DetailSensor(TypedDict):
    template_name: str
    context: dict
    
def _safe(v, placeholder="--") -> Any:
    if v is None:
        return placeholder
    if isinstance(v, str) and not v.strip():
        return placeholder
    return v

class SensorStrategy:
    """
    Devuelve un dict de configuración para cada tipo_id:
    - form_class a usar
    - template_name a renderizar
    - repo concreto para persistencia
    """
    def resolve(self, tipo_id: int) -> SensorConfig:
        # CREATE
        if tipo_id == 2:
            return {
                "form_class": SensorTPForm,
                "template_name": "sensors/create_tpsensor.html",
                "repo": SensorTPRepository(),
            }
        raise ValueError(f"No hay Strategy/Repo para tipo_id={tipo_id}")

    def resolve_update(self, tipo_id: int) -> SensorConfig:
        # UPDATE
        if tipo_id == 2:
            return {
                "form_class": SensorTPForm,
                "template_name": "sensors/update_tpsensor.html",
                "repo": SensorTPRepository(),
            }
        raise ValueError(f"No hay Strategy/Repo (update) para tipo_id={tipo_id}")
    
class ConnectionEvalStrategy:
    """
    Decide el repositorio/método de evaluación según tipoSensor.
    """
    def __init__(self):
        self.repo = SensorTPEvalConnRepository()

    def resolve_eval_callable(self, *, tipo_id: int) -> Callable:
        # tipo 2 -> gauge TP (tu sensor actual)
        if tipo_id == 2:
            return self.repo.eval_conn_tp_gauge
        # Agrega más tipos aquí
        # default: evaluar como TP gauge
        return self.repo.eval_conn_tp_gauge
    
    
class SensorDetailStrategy:
    def __init__(self):
        self.repo = SensorTPDetailRepository()

    def resolve(self, *, sensor_id: int, tipo_id: int) -> DetailSensor:
        if tipo_id == 2:
            return cast(DetailSensor, self.repo.build_detail_pres2(sensor_id))
        # Agrega aquí otros sensores.
        return cast(DetailSensor, { # default case
            "template_name": "cruds/sensores/sensor_type2_detail.html",
            "context": {},
        })
        
class SelectpDataStrategy:
    """
    Selecciona qué list armar según la 'estrategia' solicitada.
    """
    def __init__(self):
        self.repo = GasDashboardRepository()

    def run(self, *, sensor_id: int, strategy: str, extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Retorna un dict de contexto que la vista usará para el dashboard.
        """
        match strategy:
            case "latest_5_reg":
                return self.repo.latest_5_reg(sensor_id=sensor_id)
            case _:
                # fallback por si llegan estrategias futuras
                return self.repo.latest_5_reg(sensor_id=sensor_id)