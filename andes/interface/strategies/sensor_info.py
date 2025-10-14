# andes/interface/strategies/sensor_info.py
from typing import Dict, Any
from ..repositories.sen_info_tp import SentpRepository
from .chosen_maths_strategy import ChosenMathsStrategy

class SensorInfoStrategy:
    """Orquesta lectura por tipo de sensor y consolida respuesta uniforme (dict)."""
    def __init__(self):
        self.repo_tp = SentpRepository()
        self.maths = ChosenMathsStrategy()

    def resolve(self, *, sensor_id: int, tipo_id: int) -> Dict[str, Any]:
        """Elije cuál es el método para extraer los datos a partir del tipo de sensor."""
        data: Dict[str, Any] | None = None
        if tipo_id == 2:
            data = self.repo_tp.read_info(tipo_sensor=tipo_id, sensor_id=sensor_id)

            if not data:
                # estructura uniforme aunque no hayan warnings
                print(f"DEBUG: No data for sensor_id={sensor_id}, returning None structure")  # Diagnostic log
                return {
                    "sensor_id": sensor_id,
                    "tipo_id": tipo_id,
                    "data": None,
                    "math_bucket": None,
                }

            # si retorna info, añade el sensor.pk al dict
            data["sensor_id"] = sensor_id
            # ejecuta calculos
            bucket = self.maths.gas_maths_strategy(info=data)
            print(f"DEBUG: sensor_id={sensor_id}, returning data structure with data and bucket")  # Diagnostic log

            return {
                "sensor_id": sensor_id,
                "tipo_id": tipo_id,
                "data": data,            # processed_data
                "math_bucket": bucket,   # results maths
            }
                
        # añade otros tipos en el futuro
        else:
            # para tipos no soportados aún
            return {
                "sensor_id": sensor_id,
                "tipo_id": tipo_id,
                "data": None,
                "math_bucket": None,
            }

            