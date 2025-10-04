from typing import TypedDict, Type
from django import forms
from interface.forms.tp_sensor import SensorTPForm
from ..repositories.sensor_repo import SensorTPRepository

class SensorConfig(TypedDict):
    form_class: Type[forms.Form]
    template_name: str
    repo: SensorTPRepository

class SensorStrategy:
    """
    Devuelve un dict de configuración para cada tipo_id:
    - form_class a usar
    - template_name a renderizar
    - repo concreto para persistencia
    """
    def resolve(self, tipo_id: int) -> SensorConfig:
        # create different sensors
        if tipo_id == 2:
            return {
                "form_class": SensorTPForm,
                "template_name": "sensors/create_tpsensor.html",
                "repo": SensorTPRepository(),
            }
        # Agrega aquí otros mapeos de tipos
        raise ValueError(f"No hay Strategy/Repo para tipo_id={tipo_id}")
    
    def resolve_update(self, tipo_id: int) -> SensorConfig:
        # update different sensors
        if tipo_id == 2:
            return {
                "form_class": SensorTPForm,
                "template_name": "sensors/update_tpsensor.html",
                "repo": SensorTPRepository(),
            }
        # Agrega aquí otros mapeos de tipos
        raise ValueError(f"No hay Strategy/Repo (update) para tipo_id={tipo_id}")