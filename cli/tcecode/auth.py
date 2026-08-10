"""Autenticação via Keycloak — Resource Owner Password Credentials Grant."""

import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

from .config import TCE_HOME, TOKEN_FILE

CLIENT_ID = "tcecode-cli"


def _ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _post(url: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, context=_ssl_ctx(), timeout=15) as resp:
        return json.loads(resp.read())


def load_token() -> Optional[dict]:
    if TOKEN_FILE.exists():
        return json.loads(TOKEN_FILE.read_text())
    return None


def save_token(token_data: dict) -> None:
    TCE_HOME.mkdir(parents=True, exist_ok=True)
    token_data = dict(token_data)
    token_data["expires_at"] = time.time() + token_data.get("expires_in", 300) - 30
    TOKEN_FILE.write_text(json.dumps(token_data, indent=2))
    TOKEN_FILE.chmod(0o600)


def clear_token() -> None:
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()


def get_valid_token(keycloak_realm_url: str) -> Optional[str]:
    """Retorna access_token válido, renovando via refresh se necessário."""
    token = load_token()
    if not token:
        return None
    if time.time() < token.get("expires_at", 0):
        return token["access_token"]
    refresh_tok = token.get("refresh_token")
    if not refresh_tok:
        return None
    try:
        new_token = _post(
            f"{keycloak_realm_url}/protocol/openid-connect/token",
            {"client_id": CLIENT_ID, "grant_type": "refresh_token", "refresh_token": refresh_tok},
        )
        save_token(new_token)
        return new_token["access_token"]
    except Exception:
        return None


def password_login(keycloak_realm_url: str, username: str, password: str) -> dict:
    """Autentica com usuário e senha — Resource Owner Password Credentials Grant."""
    try:
        return _post(
            f"{keycloak_realm_url}/protocol/openid-connect/token",
            {
                "client_id": CLIENT_ID,
                "grant_type": "password",
                "username": username,
                "password": password,
                "scope": "openid profile email",
            },
        )
    except urllib.error.HTTPError as exc:
        body = json.loads(exc.read())
        raise RuntimeError(body.get("error_description", body.get("error", "Falha na autenticação")))
