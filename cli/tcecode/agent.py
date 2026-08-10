"""Gerenciamento do engine interno (OpenCode) — detalhe de implementação."""

import json
import os
import platform
import shutil
import stat
import subprocess
import urllib.request
from pathlib import Path

from .config import AGENT_BIN, BIN_DIR, TCE_HOME

APPROVED_VERSION = "0.1.72"

def _fork_bin_path() -> Path:
    """Retorna o path do binário compilado do fork para a plataforma atual."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch = "arm64" if machine in ("arm64", "aarch64") else "x64"
    os_name = "darwin" if system == "darwin" else "linux"
    dist_name = f"opencode-{os_name}-{arch}"
    return Path(__file__).parent.parent.parent / "opencode" / "packages" / "opencode" / "dist" / dist_name / "bin" / "tcecode-agent"

_FORK_BIN = _fork_bin_path()

# Fallback: locais onde o OpenCode pode já estar instalado no sistema
_WELL_KNOWN_PATHS = [
    Path.home() / ".opencode" / "bin" / "opencode",
    Path("/usr/local/bin/opencode"),
    Path("/opt/homebrew/bin/opencode"),
]


def _find_system_opencode() -> Path | None:
    """Procura tcecode-agent ou opencode já instalado."""
    # Primeiro: binário do fork local
    if _FORK_BIN.exists() and os.access(_FORK_BIN, os.X_OK):
        return _FORK_BIN
    # Fallback: sistema
    found = shutil.which("opencode")
    if found:
        return Path(found)
    for p in _WELL_KNOWN_PATHS:
        if p.exists() and os.access(p, os.X_OK):
            return p
    return None


def agent_ok() -> bool:
    if AGENT_BIN.exists() and os.access(AGENT_BIN, os.X_OK):
        return True
    # Fallback: detectar instalação do sistema e vincular
    system_bin = _find_system_opencode()
    if system_bin:
        _link_system_bin(system_bin)
        return True
    return False


def _link_system_bin(system_bin: Path) -> None:
    """Vincula o binary do sistema ao diretório gerenciado pelo tcecode."""
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    if AGENT_BIN.exists() or AGENT_BIN.is_symlink():
        AGENT_BIN.unlink()
    AGENT_BIN.symlink_to(system_bin)
    # Registrar versão
    try:
        result = subprocess.run([str(system_bin), "--version"], capture_output=True, text=True, timeout=5)
        version = result.stdout.strip() or result.stderr.strip() or "unknown"
    except Exception:
        version = "unknown"
    versions_file = TCE_HOME / "versions.json"
    versions_file.write_text(json.dumps({"opencode": {"installed": version, "source": str(system_bin)}}, indent=2))


def agent_path() -> Path:
    if not agent_ok():
        raise RuntimeError("Engine não instalado. Execute: tcecode update")
    return AGENT_BIN


def _platform_asset() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch = "arm64" if machine in ("arm64", "aarch64") else "x86_64"
    if system == "darwin":
        return f"opencode-{arch}-apple-darwin.tar.gz"
    if system == "linux":
        return f"opencode-{arch}-unknown-linux-musl.tar.gz"
    raise RuntimeError(f"Sistema não suportado: {system}/{machine}")


def install_agent(version: str = APPROVED_VERSION) -> None:
    """Baixa e instala o engine na versão aprovada."""
    # Tentar primeiro usar instalação existente no sistema
    system_bin = _find_system_opencode()
    if system_bin:
        print(f"Engine encontrado em {system_bin} — vinculando...")
        _link_system_bin(system_bin)
        return

    # Download do GitHub
    asset = _platform_asset()
    url = f"https://github.com/sst/opencode/releases/download/v{version}/{asset}"
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    tmp_archive = BIN_DIR / asset

    print(f"Baixando tcecode engine v{version}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "tcecode/0.1"})
        with urllib.request.urlopen(req, timeout=60) as resp, open(tmp_archive, "wb") as f:
            f.write(resp.read())
    except Exception as e:
        tmp_archive.unlink(missing_ok=True)
        raise RuntimeError(
            f"Falha ao baixar engine: {e}\n"
            "Instale o OpenCode manualmente: https://opencode.ai\n"
            "Depois rode 'tcecode update' novamente."
        ) from e

    # Extrair
    import tarfile
    with tarfile.open(tmp_archive) as tar:
        tar.extractall(BIN_DIR)
    tmp_archive.unlink(missing_ok=True)

    # Localizar binary extraído
    candidates = list(BIN_DIR.glob("opencode*"))
    binary = next((c for c in candidates if os.access(c, os.X_OK) and c != AGENT_BIN), None)
    if binary and binary != AGENT_BIN:
        binary.rename(AGENT_BIN)

    AGENT_BIN.chmod(AGENT_BIN.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    versions_file = TCE_HOME / "versions.json"
    versions_file.write_text(json.dumps({"opencode": {"installed": version, "approved": version}}, indent=2))
    print(f"Engine instalado em {AGENT_BIN}")


def installed_version() -> str | None:
    versions_file = TCE_HOME / "versions.json"
    if not versions_file.exists():
        return None
    data = json.loads(versions_file.read_text())
    return data.get("opencode", {}).get("installed")
