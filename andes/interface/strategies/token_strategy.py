from typing import Protocol, Mapping, Any, cast
from ..adapters.auth_TPserver import ToprieAuthAdapter

class TokenStrategy(Protocol):
    """Interfaz común para obtener token y devolver el JSON crudo del proveedor."""
    def fetch(self, *, username: str, password: str, authorization: str) -> Mapping[str, Any]:
        ...

class ToprieTokenStrategy(TokenStrategy):
    def __init__(self, adapter: ToprieAuthAdapter | None = None):
        self.adapter = adapter or ToprieAuthAdapter()

    def fetch(self, *, username: str, password: str, authorization: str) -> Mapping[str, Any]:
        return self.adapter.get_access_token(
            username=username,
            password=password,
            authorization_basic=authorization,
        )

# Router simple por id de credencial
def resolve_token_strategy_for_credential(cred_id: int) -> TokenStrategy:
    # En el futuro se deben mapear más ids a más estrategias.
    if cred_id == 1:
        return ToprieTokenStrategy()
    return ToprieTokenStrategy()