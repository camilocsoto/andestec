from dataclasses import dataclass
from typing import cast
from django.db import transaction
from django.utils import timezone
from ..models import ServerCredentials
from ..strategies.token_strategy import resolve_token_strategy_for_credential

@dataclass
class TokenService:
    """
    Orquesta:
    - Cargar credencial,
    - Resolver strategy,
    - Llamar adapter vía strategy,
    - Guardar server_access_token = "bearer <token>" y token_updated.
    """
    def refresh_single(self, cred_id: int) -> ServerCredentials:
        with transaction.atomic():
            cred = ServerCredentials.objects.select_for_update().get(pk=cred_id)
            # defensiva minima: evita None en credenciales
            if cred.user is None or cred.password is None or cred.authorization is None:
                raise ValueError(f'credenciales incompletas: {cred.user}, {cred.password}, {cred.authorization}')
            
            strategy = resolve_token_strategy_for_credential(cred_id)
            username= cast(str, cred.user) 
            password=cast(str, cred.password)
            authorization=cast(str, cred.authorization)
            token_json = strategy.fetch(
                username=username,
                password=password,
                authorization=authorization,
            )
            
            access = token_json["access_token"]
            cred.server_access_token = f"bearer {access}"  # guardar con prefijo
            cred.token_updated = timezone.now()
            # Si quieres validar que clientId/userId coinciden con los de la fila, puedes hacerlo aquí.
            cred.save(update_fields=["server_access_token", "token_updated"])
            return cred
