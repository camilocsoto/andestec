import requests
from typing import Mapping, Any, cast

class ToprieAuthAdapter:
    """
    Adapter del endpoint de token (grant_type=password).
    """
    def __init__(self, base_url: str = "https://app.dtuip.com"):
        self.base_url = base_url.rstrip("/")

    def get_access_token( self, username: str, password: str, authorization_basic: str) -> Mapping[str, Any]:
        url = f"{self.base_url}/oauth/token"
        params = { "grant_type": "password", "username": username, "password": password}
        headers = { "Authorization": authorization_basic }
        r = requests.post(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return cast(Mapping[str,Any], data)
