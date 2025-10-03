from celery import shared_task
from ..services.tokenServiceTP import TokenService

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def refresh_toprie_credential(self, cred_id: int = 1):
    """
    Actualiza SOLO la credencial indicada (por defecto id=1).
    Guarda server_access_token='bearer <...>' y token_updated.
    """
    try:
        service = TokenService()
        cred = service.refresh_single(cred_id=cred_id)
        return {"ok": True, "cred_id": cred.pk, "updated_at": str(cred.token_updated)}
    except Exception as exc:
        # Reintento ante fallos transitorios
        raise self.retry(exc=exc)
