#!/usr/bin/env bash
# Instalador do tcecode — Linux e macOS.
#
# Uso:
#   curl -fsSL https://bitbucket.org/tcesc-git/tcecode/raw/master/scripts/install.sh | bash
#
# Clona o repositório institucional (CLI + fork do OpenCode) e builda o
# tcecode-agent localmente com Bun. Não depende de binário pré-buildado —
# o build leva alguns minutos na primeira instalação.

set -euo pipefail

REPO_SSH="git@bitbucket.org:tcesc-git/tcecode.git"
REPO_HTTPS="https://bitbucket.org/tcesc-git/tcecode.git"
FORK_SSH="git@github.com:brenothales/opencode.git"
FORK_HTTPS="https://github.com/brenothales/opencode.git"
FORK_BRANCH="dev"

# O agent.py resolve o caminho do fork como .../<repo>/opencode/packages/opencode/dist/...
# relativo ao próprio clone (import editável) — por isso mantemos um clone
# persistente aqui, em vez de instalar via pip solto.
INSTALL_DIR="${TCECODE_SRC_DIR:-$HOME/.local/share/tcecode-src}"

echo "==> Instalando tcecode em ${INSTALL_DIR}..."

if ! command -v python3 &>/dev/null; then
  echo "Erro: python3 não encontrado. Instale Python 3.10+ antes de continuar." >&2
  exit 1
fi

if ! command -v pipx &>/dev/null; then
  echo "==> pipx não encontrado, instalando..."
  if command -v apt &>/dev/null; then
    sudo apt update -qq && sudo apt install -y pipx
  elif command -v brew &>/dev/null; then
    brew install pipx
  elif command -v dnf &>/dev/null; then
    sudo dnf install -y pipx
  else
    python3 -m pip install --user pipx
  fi
  python3 -m pipx ensurepath
fi

use_ssh() {
  ssh -T git@bitbucket.org -o BatchMode=yes -o ConnectTimeout=5 2>&1 | grep -qi "authenticated\|logged in"
}

if use_ssh; then
  REPO_URL="$REPO_SSH"
  FORK_URL="$FORK_SSH"
else
  echo "Aviso: SSH para bitbucket.org não configurado — usando HTTPS (pode pedir credenciais)."
  REPO_URL="$REPO_HTTPS"
  FORK_URL="$FORK_HTTPS"
fi

echo "==> Clonando/atualizando ${REPO_URL}..."
if [[ -d "$INSTALL_DIR/.git" ]]; then
  git -C "$INSTALL_DIR" pull --ff-only
else
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

echo "==> Clonando/atualizando o fork do OpenCode (${FORK_BRANCH})..."
FORK_DIR="$INSTALL_DIR/opencode"
if [[ -d "$FORK_DIR/.git" ]]; then
  git -C "$FORK_DIR" pull --ff-only
else
  rmdir "$FORK_DIR" 2>/dev/null || true
  git clone --branch "$FORK_BRANCH" --depth 1 "$FORK_URL" "$FORK_DIR"
fi

if ! command -v bun &>/dev/null; then
  echo "==> Bun não encontrado, instalando..."
  curl -fsSL https://bun.sh/install | bash
  export PATH="$HOME/.bun/bin:$PATH"
fi

echo "==> Buildando tcecode-agent (isso pode levar alguns minutos na primeira vez)..."
(
  cd "$FORK_DIR/packages/opencode"
  bun install
  bun run script/build.ts --single --skip-embed-web-ui
)

echo "==> Instalando o CLI tcecode (editável, via pipx)..."
pipx install --force -e "$INSTALL_DIR/cli"

hash -r
tcecode update

echo ""
echo "==> tcecode instalado! Rode 'tcecode login' para autenticar e 'tcecode configure' para configurar sua squad."
