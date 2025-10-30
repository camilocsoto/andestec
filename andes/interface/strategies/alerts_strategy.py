# interface/strategies/alerts_strategy.py
import logging
from typing import Optional
from django.utils import timezone
from interface.models import Sensor
from interface.repositories.alarms_repo import AlarmsRepository

logger = logging.getLogger(__name__)


class AlertsStrategy:
    """
    Reglas:
      - Inactivo: sensor_is_up is False (o None) -> code=1
      - Poco gas: mass_left_kg < threshold -> code=2
      - Batería baja: battery_pct < threshold -> code=3
    Ejecuta SI y solo si no hubo alarma hoy de ese tipo para ese sensor.
    """

    def __init__(self) -> None:
        self.repo = AlarmsRepository()

    def evaluate_and_dispatch(
        self,
        *,
        sensor: Sensor,
        email: Optional[str],
        sensor_is_up: Optional[bool],
        mass_left_kg: Optional[float],
        battery_pct: Optional[float],
        low_gas_threshold: float,
        low_battery_threshold: float,) -> None:

        logger.debug(f"Evaluando alertas para sensor {sensor.pk}: up={sensor_is_up}, gas={mass_left_kg}, bat={battery_pct}")

        # 1) Inactivo
        if sensor_is_up is False or sensor_is_up is None:
            logger.info(f"Alerta inactivo para sensor {sensor.pk}")
            self.repo.inactive_sensor(sensor=sensor, email=email)
            return  # Prioridad: inactivo primero

        # 2) Poco gas
        if mass_left_kg is not None and mass_left_kg < low_gas_threshold:
            logger.info(f"Alerta poco gas para sensor {sensor.pk}: {mass_left_kg} kg < {low_gas_threshold}")
            self.repo.low_gas(sensor=sensor, email=email, mass_left_kg=mass_left_kg)
            return

        # 3) Batería baja
        if battery_pct is not None and battery_pct < low_battery_threshold:
            logger.info(f"Alerta batería baja para sensor {sensor.pk}: {battery_pct}% < {low_battery_threshold}")
            self.repo.low_battery(sensor=sensor, email=email, battery_pct=battery_pct)
            return

        # No hay alertas que emitir
        logger.debug(f"No hay alertas para sensor {sensor.pk}")
        return
