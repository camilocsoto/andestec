from __future__ import annotations
from celery import shared_task
import logging
from ..services.maths import MathService

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def connect_sensor(self) -> None:
    """ Dispara la extracción de datos desde los sensores (cada 2 min)."""
    try:
        results = MathService().extract_data()
        logger.info("eval_connect_sensor OK | items=%s", len(results))
        # Diagnostic: log details of results
        for i, res in enumerate(results):
            logger.info("Result %d: sensor_id=%s, tipo_id=%s, has_data=%s, has_math_bucket=%s",
                       i, res.get('sensor_id'), res.get('tipo_id'),
                       res.get('data') is not None, res.get('math_bucket') is not None)
            if res.get('data'):
                logger.info("Data details: pressure=%s, temperature=%s, heartbeat=%s",
                           res['data'].get('pressure'), res['data'].get('temperature'),
                           res['data'].get('heartbeatDate'))
    except Exception:
        logger.exception("eval_connect_sensor: error")
        raise