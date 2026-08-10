"""Configuração do tce-ai CLI."""

import os
from pathlib import Path
from dataclasses import dataclass, field
import json


CONFIG_DIR = Path.home() / ".tce-ai"
CONFIG_FILE = CONFIG_DIR / "config.json"
TOKEN_FILE = CONFIG_DIR / "token.json"
OPENCODE_CONFIG = Path.home() / ".opencode" / "config.json"

GATEWAY_URL = os.environ.get("TCE_AI_GATEWAY_URL", "http://localhost:4000")
DEFAULT_MODEL = os.environ.get("TCE_AI_DEFAULT_MODEL", "institutional-coding")


@dataclass
class TceAiConfig:
    gateway_url: str = GATEWAY_URL
    default_model: str = DEFAULT_MODEL
    squad: str = ""
    project: str = ""
    virtual_key: str = ""  # Fase 1: virtual key por squad (sem Keycloak)


def load_config() -> TceAiConfig:
    if not CONFIG_FILE.exists():
        return TceAiConfig()
    data = json.loads(CONFIG_FILE.read_text())
    return TceAiConfig(**data)


def save_config(cfg: TceAiConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg.__dict__, indent=2))
    CONFIG_FILE.chmod(0o600)


def write_opencode_config(cfg: TceAiConfig, api_key: str) -> None:
    """Configura o OpenCode para usar o AI Gateway institucional."""
    opencode_cfg = {
        "providers": {
            "openai": {
                "apiKey": api_key,
                "baseURL": f"{cfg.gateway_url}/v1",
            }
        },
        "model": f"openai/{cfg.default_model}",
    }
    OPENCODE_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    OPENCODE_CONFIG.write_text(json.dumps(opencode_cfg, indent=2))
    OPENCODE_CONFIG.chmod(0o600)
