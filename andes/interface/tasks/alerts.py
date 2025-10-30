import logging
from celery import shared_task
from django.db.models import Prefetch
from interface.models import Sensor, GasRestante, CaracteristicasCilindro
from interface.services.alarm_service import AlarmService

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def scan_sensors_and_raise_alerts() -> None:
    """
    Itera sensores y delega en el servicio de alarmas.
    No usamos async: Celery ya paraleliza con workers.
    """
    logger.info("Iniciando tarea scan_sensors_and_raise_alerts")
    try:
        # Cargar relaciones necesarias:
        # - OneToOne: usar select_related('gasrestante')
        # - FK Empresa→Usuario: select_related('empresa__usuario')
        # - Cylinders del GasRestante: prefetch al reverse 'caracteristicascilindro_set'
        qs = (
            Sensor.objects
            .select_related("empresa__usuario", "gasrestante")
            .prefetch_related(
                Prefetch(
                    # desde Sensor → gasrestante (O2O) → caracteristicascilindro_set (reverse FK)
                    "gasrestante__caracteristicascilindro_set",
                    queryset=CaracteristicasCilindro.objects.only(
                        "id", "masa_gas_restant_kg", "GasRestante_id"
                    ),
                    to_attr="pref_cyls"  # atributo que quedará en cada instancia de GasRestante
                )
            )
        )

        total = qs.count()
        logger.info(f"Query preparada, sensores a procesar: {total}")

        for sensor in qs.iterator(chunk_size=200):
            logger.debug("Procesando sensor ID=%s, nombre=%s", sensor.pk, sensor.nombre)
            try:
                # El service ya sabe leer: sensor.gasrestante (O2O)
                # y, si existe, sensor.gasrestante.pref_cyls (lista de cilindros prefetchados)
                AlarmService.scan_sensor(sensor)
            except Exception as e:
                logger.error("Error procesando sensor %s: %s", sensor.pk, e, exc_info=True)

        logger.info("Tarea scan_sensors_and_raise_alerts completada exitosamente")
    except Exception as e:
        logger.error("Error general en tarea scan_sensors_and_raise_alerts: %s", e, exc_info=True)
        raise