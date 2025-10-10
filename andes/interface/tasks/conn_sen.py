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
    except Exception:
        logger.exception("eval_connect_sensor: error")
        raise