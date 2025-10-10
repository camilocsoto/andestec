from typing import Optional, Dict, Any
from django.utils import timezone
from django.db import transaction
from datetime import datetime
from ..models import Sensor, GasRestante, CaracteristicasCilindro, ResultsGasRestante, ServerCredentials

from ..adapters.toprie_info import ToprieInfoAdapter

class SentpRepository:
    """ Lee info de sensor tipo TP (tipo_id=2) desde el proveedor y decide si hay novedad."""

    def _get_gas_by_sensor(self, sensor_id: int) -> Optional[GasRestante]:
        try:
            return (GasRestante.objects.select_related("Sensor_idSensor", "server_credentials").get(Sensor_idSensor_id=sensor_id))
        except GasRestante.DoesNotExist:
            return None

    def _get_primary_cylinder(self, gas: GasRestante) -> Optional[CaracteristicasCilindro]:
        return (CaracteristicasCilindro.objects.select_related("GasRestante").filter(GasRestante=gas).order_by("pk").first())

    def _latest_result_ts_for_cyl(self, cyl: CaracteristicasCilindro) -> Optional[datetime]:
        last = (ResultsGasRestante.objects.filter(CaracterísticasCilindro=cyl, timestamp__isnull=False).order_by("-timestamp").only("timestamp").first())
        return last.timestamp if last else None

    def _parse_heartbeat_tzaware(self, raw: str | None) -> Optional[datetime]:
        """
        Convierte "YYYY-MM-DD HH:MM:SS" a datetime 'aware' en TZ local.
        """
        if not raw:
            return None
        try:
            dt_naive = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")
            return timezone.make_aware(dt_naive, timezone.get_current_timezone())
        except Exception:
            return None

    @transaction.atomic
    def read_info(self, *, tipo_sensor: int, sensor_id: int) -> Dict[str, Any] | None:
        """
        Devuelve processed_data (dict) si hay novedad; si no, None.
        """
        # 1) Navega relaciones: Sensor -> GasRestante -> ServerCredentials
        gas = self._get_gas_by_sensor(sensor_id)
        if gas is None or gas.server_credentials.pk is None:
            return None

        creds: ServerCredentials = gas.server_credentials
        server_clientId = getattr(creds, "server_clientId", None)
        authorization   = getattr(creds, "server_access_token", None)
        server_userId   = getattr(creds, "server_userId", None)
        device_no       = getattr(gas,   "server_deviceNo", None)

        if not (server_clientId and authorization and server_userId and device_no):
            return None

        # 2) Llama adapter y transforma
        adapter = ToprieInfoAdapter(
            server_clientId=server_clientId,
            authorization=authorization,
            server_userId=server_userId,
            server_deviceNo=device_no,
        )
        processed = adapter.transform_info()
        if not processed:
            return None

        # 3) Compara heartbeatDate con último Results.timestamp
        cyl = self._get_primary_cylinder(gas)
        if cyl is None:
            return None

        last_ts = self._latest_result_ts_for_cyl(cyl)   # datetime | None
        hb_ts   = self._parse_heartbeat_tzaware(processed.get("heartbeatDate"))

        # Regla: si no hay último (None) o es IGUAL al heartbeat => NO hay novedad
        if last_ts is None or (hb_ts is not None and last_ts == hb_ts):
            return None

        # Hay novedad -> retorna dict uniforme (processed_data)
        return processed
