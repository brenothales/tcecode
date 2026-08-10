"""Configuração do tcecode."""

import json
import os
from dataclasses import dataclass
from pathlib import Path

TCE_HOME = Path.home() / ".tcecode"
CONFIG_FILE = TCE_HOME / "config.json"
TOKEN_FILE = TCE_HOME / "token.json"
BIN_DIR = TCE_HOME / "bin"
AGENT_BIN = BIN_DIR / "tcecode-agent"

GATEWAY_URL = os.environ.get("TCECODE_GATEWAY_URL", "https://localhost/v1")
DEFAULT_MODEL = os.environ.get("TCECODE_MODEL", "institutional-coding")
KEYCLOAK_URL = os.environ.get("TCECODE_KEYCLOAK_URL", "https://localhost/auth/realms/tce-ai")


@dataclass
class TceCodeConfig:
    gateway_url: str = GATEWAY_URL
    default_model: str = DEFAULT_MODEL
    squad: str = ""
    virtual_key: str = ""  # Fase 1 — substituído por JWT na Fase 2
    keycloak_url: str = ""


def load_config() -> TceCodeConfig:
    if not CONFIG_FILE.exists():
        return TceCodeConfig()
    data = json.loads(CONFIG_FILE.read_text())
    return TceCodeConfig(**{k: v for k, v in data.items() if k in TceCodeConfig.__dataclass_fields__})


def save_config(cfg: TceCodeConfig) -> None:
    TCE_HOME.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg.__dict__, indent=2))
    CONFIG_FILE.chmod(0o600)


def _fetch_gateway_models(gateway_url: str, api_key: str) -> dict:
    """Busca modelos disponíveis no gateway e retorna dict para o config do agent."""
    import ssl
    import urllib.request
    import urllib.error

    url = gateway_url.rstrip("/").removesuffix("/v1") + "/v1/models"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            data = json.loads(resp.read())
        return {m["id"]: {"name": m["id"].replace("-", " ").title()} for m in data.get("data", [])}
    except Exception:
        return {}


def write_agent_config(cfg: TceCodeConfig, api_key: str) -> None:
    """Configura o engine interno para usar o AI Gateway institucional."""
    xdg_config = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    agent_cfg_dir = xdg_config / "tcecode"
    agent_cfg_dir.mkdir(parents=True, exist_ok=True)

    # Declara os modelos explicitamente — quando baseURL é customizada o OpenCode
    # desabilita autoload (provider.ts:732), então os modelos não aparecem na TUI.
    models = _fetch_gateway_models(cfg.gateway_url, api_key)

    # v1 config format: key "provider" (singular) — lido pelo provider.ts interno
    # options.apiKey e options.baseURL são mapeados corretamente pelo ConfigProviderOptionsV1
    # "npm" é obrigatório: sem ele, ConfigProviderOptionsV1.get() cai no lowerer "raw" e
    # nunca gera o header Authorization (apiKey vai parar dentro do body, sem efeito) —
    # ver v1/config/migrate.ts:171 e v1/config/provider-options.ts:17-27.
    # whitelist filtra modelos do catálogo models.dev para só mostrar os institucionais
    provider_cfg: dict = {
        "npm": "@ai-sdk/openai",
        "options": {"apiKey": api_key, "baseURL": cfg.gateway_url},
    }
    if models:
        provider_cfg["models"] = models
        provider_cfg["whitelist"] = list(models.keys())

    agent_cfg = {
        "provider": {"openai": provider_cfg},
        "model": f"openai/{cfg.default_model}",
    }
    agent_cfg_file = agent_cfg_dir / "config.json"
    agent_cfg_file.write_text(json.dumps(agent_cfg, indent=2))
    agent_cfg_file.chmod(0o600)
