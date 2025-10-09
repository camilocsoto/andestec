from __future__ import annotations
from celery import shared_task
import logging
from ..services.sensor import SensorService

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def eval_connection(self) -> None:
    """
    Revisa todos los sensores y marca estado (UP/DOWN) según tolerancia y último dato.
    """
    try:
        SensorService().eval_conn()
        logger.info("eval_connection: OK")
    except Exception as exc:
        logger.exception("eval_connection: error")
        raise