# andes/interface/services/maths.py
from dataclasses import dataclass
from typing import List, Dict, Any
from django.db.models import QuerySet
from ..models import Sensor
from ..strategies.sensor_info import SensorInfoStrategy

@dataclass
class MathService:
    def extract_data(self) -> List[Dict[str, Any]]:
        """
        Itera get_info a cada sensor y, por strategy, intenta leer info del proveedor.
        Devuelve lista de dicts con estructura uniforme:
        {
          "sensor_id": int,
          "tipo_id": int,
          "data": dict | None,        # processed_data si hay novedad; None si no hay
          "math_bucket": int | None,  # group of calculations
        }
        """
        out: List[Dict[str, Any]] = []
        qs: QuerySet[Sensor] = Sensor.objects.select_related("tipoSensor").all()
        strat = SensorInfoStrategy()

        for s in qs:
            tipo_id = s.tipoSensor.pk
            item = strat.resolve(sensor_id=s.pk, tipo_id=tipo_id)
            # item SIEMPRE es dict con las mismas llaves
            out.append(item)

        return out