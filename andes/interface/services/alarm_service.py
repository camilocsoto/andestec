# interface/services/alarm_service.py
from __future__ import annotations
import logging
from typing import Optional, Tuple, cast
from django.utils import timezone
from django.db.models import Q
from interface.models import Sensor, GasRestante, CaracteristicasCilindro
from interface.strategies.alerts_strategy import AlertsStrategy

logger = logging.getLogger(__name__)


LOW_GAS_THRESHOLD_KG = 1.3
LOW_BATTERY_THRESHOLD = 30.0  # "30" -> 30.0


class AlarmService:
    """
    Lee datos del sensor y sus relaciones, resuelve correo del dueño y delega en la estrategia.
    """

    @staticmethod
    def _get_company_email(sensor: Sensor) -> Optional[str]:
        logger.debug(f"Obteniendo email para sensor {sensor.pk}")
        if sensor is not None:
            logger.warning(f"Sensor {sensor.pk} es None")
            return None
        sensor=cast(Sensor,sensor)
        try:
            email = sensor.empresa.usuario.email
            logger.debug(f"Email obtenido: {email}")
            return email  # usuario is not attribute of none.
        except Exception as e:
            logger.error(f"Error obteniendo email para sensor {sensor.pk}: {e}", exc_info=True)
            return None

    @staticmethod
    def _get_gas(sensor: Sensor) -> Optional[GasRestante]:
        logger.debug(f"Obteniendo GasRestante para sensor {sensor.pk}")
        # Por compatibilidad con OneToOne sin related_name explícito: - Si existe atributo directo
        if hasattr(sensor, "gasrestante"):
            gas = getattr(sensor, "gasrestante", None)
            logger.debug(f"GasRestante encontrado via atributo directo: {gas}")
            return gas
        # - Si vino prefetch a mano (por el task)
        if hasattr(sensor, "pref_gas"):
            lst = getattr(sensor, "pref_gas") or []
            gas = lst[0] if lst else None
            logger.debug(f"GasRestante encontrado via prefetch: {gas}")
            return gas
        # - Fallback a query
        try:
            gas = GasRestante.objects.filter(Sensor_idSensor=sensor).first()
            logger.debug(f"GasRestante encontrado via query: {gas}")
            return gas
        except Exception as e:
            logger.error(f"Error en query GasRestante para sensor {sensor.pk}: {e}", exc_info=True)
            return None

    @staticmethod
    def _get_primary_cylinder(gas: GasRestante) -> Optional[CaracteristicasCilindro]:
        logger.debug(f"Obteniendo cilindro primario para GasRestante {gas.pk}")
        try:
            cyl = CaracteristicasCilindro.objects.filter(GasRestante=gas).order_by("id").first()
            logger.debug(f"Cilindro encontrado: {cyl}")
            return cyl
        except Exception as e:
            logger.error(f"Error obteniendo cilindro para GasRestante {gas.pk}: {e}", exc_info=True)
            return None

    @staticmethod
    def _binary_to_bool(bval) -> Optional[bool]:
        if bval is None:
            return None
        if isinstance(bval, (bytes, bytearray, memoryview)):
            data = bytes(bval) if not isinstance(bval, (bytes, bytearray)) else bval
            if len(data) == 0:
                return None
            # Convención: 0x00=false, otro=true
            return data != b"\x00"
        # si alguien cambió a BooleanField:
        if isinstance(bval, bool):
            return bval
        return None

    @classmethod
    def scan_sensor(cls, sensor: Sensor) -> None:
        """
        Recolecta datos del sensor y decide qué reglas evaluar.
        Delega al strategy. No persiste aquí.
        """
        logger.info(f"Iniciando scan_sensor para sensor {sensor.pk}")
        try:
            email = cls._get_company_email(sensor)
            gas = cls._get_gas(sensor)

            # estado del sensor (BinaryField o BooleanField)
            sensor_is_up = cls._binary_to_bool(sensor.estado)
            logger.debug(f"Sensor {sensor.pk} estado: {sensor_is_up}")

            # batería (string numérica o None)
            battery_pct: Optional[float] = None
            if gas and gas.bateria:
                try:
                    battery_pct = float(str(gas.bateria).strip().replace("%", ""))
                    logger.debug(f"Batería sensor {sensor.pk}: {battery_pct}%")
                except Exception as e:
                    logger.warning(f"Error parseando batería sensor {sensor.pk}: {e}")
                    battery_pct = None

            # masa gas restante (desde CaracteristicasCilindro)
            mass_left: Optional[float] = None
            cyl = cls._get_primary_cylinder(gas) if gas else None
            if cyl and cyl.masa_gas_restant_kg is not None:
                try:
                    mass_left = float(cyl.masa_gas_restant_kg)
                    logger.debug(f"Masa gas restante sensor {sensor.pk}: {mass_left} kg")
                except Exception as e:
                    logger.warning(f"Error parseando masa gas sensor {sensor.pk}: {e}")
                    mass_left = None

            # Delegar al strategy (reglas)
            logger.debug(f"Delegando a AlertsStrategy para sensor {sensor.pk}")
            strategy = AlertsStrategy()
            strategy.evaluate_and_dispatch(
                sensor=sensor,
                email=email,
                sensor_is_up=sensor_is_up,
                mass_left_kg=mass_left,
                battery_pct=battery_pct,
                low_gas_threshold=LOW_GAS_THRESHOLD_KG,
                low_battery_threshold=LOW_BATTERY_THRESHOLD,
            )
            logger.info(f"Scan_sensor completado para sensor {sensor.pk}")
        except Exception as e:
            logger.error(f"Error en scan_sensor para sensor {sensor.pk}: {e}", exc_info=True)
            raise
