# interface/repositories/alarms_repository.py
from __future__ import annotations
import logging
from typing import Optional, Tuple
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from interface.models import Alarma, Sensor
from interface.adapters.alarm_adapter import AlarmAdapters

logger = logging.getLogger(__name__)


# Códigos deseados (si 'estado' es SmallIntegerField)
CODE_INACTIVE = 1
CODE_LOW_GAS = 2
CODE_LOW_BATTERY = 3


def _is_smallint_field() -> bool:
    # Detecta si 'estado' acepta ints (SmallIntegerField) o es BooleanField
    try:
        field = Alarma._meta.get_field("estado")
        from django.db.models import SmallIntegerField, BooleanField
        return isinstance(field, SmallIntegerField)
    except Exception:
        return False


def _today_equals(dt) -> bool:
    if not dt:
        return False
    try:
        return timezone.localtime(dt).date() == timezone.localdate()
    except Exception:
        return False


class AlarmsRepository:
    """
    Crea y deduplica alarmas por día y tipo.
    Si 'estado' es SmallIntegerField → usa código 1/2/3.
    Si es BooleanField → usa True y deduplica por nombreAlarma.
    Tras crear, dispara el adaptador de notificaciones.
    """

    def __init__(self) -> None:
        self.adapter = AlarmAdapters()
        self._estado_is_smallint = _is_smallint_field()

    def _find_last(self, *, sensor: Sensor, code: int, name: str) -> Optional[Alarma]:
        logger.debug(f"Buscando última alarma para sensor {sensor.pk}, code={code}, name={name}")
        try:
            qs = Alarma.objects.filter(Sensor=sensor)
            if self._estado_is_smallint:
                qs = qs.filter(estado=code)
            else:
                # BooleanField: deduplicamos por nombre
                qs = qs.filter(nombreAlarma=name)
            last = qs.order_by("-fecha").first()
            logger.debug(f"Última alarma encontrada: {last}")
            return last
        except Exception as e:
            logger.error(f"Error buscando última alarma para sensor {sensor.pk}: {e}", exc_info=True)
            return None

    @transaction.atomic
    def _create_and_notify(
        self,
        *,
        sensor: Sensor,
        email: Optional[str],
        name: str,
        description: str,
        code: int,
    ) -> None:
        logger.info(f"Creando alarma '{name}' para sensor {sensor.pk}")
        try:
            now = timezone.now()
            estado_value = code if self._estado_is_smallint else True

            alarma = Alarma.objects.create(
                nombreAlarma=name,
                fecha=now,
                descripcion=description,
                estado=estado_value,
                Sensor=sensor,
            )
            logger.info(f"Alarma creada: {alarma.pk}")

            subject = f"[Alerta] {name} - {sensor.nombre or f'Sensor {sensor.pk}'}"
            context = {
                "sensor_name": sensor.nombre or f"Sensor {sensor.pk}",
                "empresa": getattr(sensor.empresa, "pk", None),
                "fecha": timezone.localtime(now).strftime("%Y-%m-%d %H:%M:%S"),
                "descripcion": description,
                "tipo": name,
            }
            logger.debug(f"Enviando email a {email} con subject: {subject}")
            self.adapter.send_email_html(to_email=email, subject=subject, context=context)
            logger.info(f"Notificación enviada para alarma {alarma.pk}")
        except Exception as e:
            logger.error(f"Error creando alarma para sensor {sensor.pk}: {e}", exc_info=True)
            raise

    # ----------------- Casos -----------------

    def inactive_sensor(self, *, sensor: Sensor, email: Optional[str]) -> None:
        logger.debug(f"Procesando alerta inactivo para sensor {sensor.pk}")
        name = "Sensor inactivo"
        code = CODE_INACTIVE
        last = self._find_last(sensor=sensor, code=code, name=name)
        if last and _today_equals(last.fecha):
            logger.debug(f"Alerta inactivo ya enviada hoy para sensor {sensor.pk}")
            return

        desc = (
            f"Hemos detectado que el sensor {sensor.nombre or sensor.pk} se ha quedado inactivo. "
            f"Por favor accede al panel para revisar la conexión."
        )
        self._create_and_notify(sensor=sensor, email=email, name=name, description=desc, code=code)

    def low_gas(self, *, sensor: Sensor, email: Optional[str], mass_left_kg: float) -> None:
        logger.debug(f"Procesando alerta poco gas para sensor {sensor.pk}: {mass_left_kg} kg")
        name = "Poco gas"
        code = CODE_LOW_GAS
        last = self._find_last(sensor=sensor, code=code, name=name)
        if last and _today_equals(last.fecha):
            logger.debug(f"Alerta poco gas ya enviada hoy para sensor {sensor.pk}")
            return

        desc = (
            f"El sensor {sensor.nombre or sensor.pk} indica bajo nivel de gas "
            f"(≈ {mass_left_kg:.2f} kg restantes). Programa el reemplazo del cilindro."
        )
        self._create_and_notify(sensor=sensor, email=email, name=name, description=desc, code=code)

    def low_battery(self, *, sensor: Sensor, email: Optional[str], battery_pct: float) -> None:
        logger.debug(f"Procesando alerta batería baja para sensor {sensor.pk}: {battery_pct}%")
        name = "Batería baja"
        code = CODE_LOW_BATTERY
        last = self._find_last(sensor=sensor, code=code, name=name)
        if last and _today_equals(last.fecha):
            logger.debug(f"Alerta batería baja ya enviada hoy para sensor {sensor.pk}")
            return

        desc = (
            f"El sensor {sensor.nombre or sensor.pk} reporta batería baja "
            f"({battery_pct:.0f}%). Considera reemplazarla o recargarla."
        )
        self._create_and_notify(sensor=sensor, email=email, name=name, description=desc, code=code)
