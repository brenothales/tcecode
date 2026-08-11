#!/usr/bin/env bash
# Instalador do tcecode — Linux e macOS.
#
# Uso:
#   curl -fsSL https://bitbucket.org/tcesc-git/tcecode/raw/main/scripts/install.sh | bash
#
# Instala o CLI `tcecode` (via pipx, direto do repositório) e o engine
# tcecode-agent (binário publicado em Bitbucket Downloads pelo bitbucket-pipelines.yml).

set -euo pipefail

REPO_SSH="git+ssh://git@bitbucket.org/tcesc-git/tcecode.git#subdirectory=cli"
REPO_HTTPS="git+https://bitbucket.org/tcesc-git/tcecode.git#subdirectory=cli"

echo "==> Instalando tcecode..."

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

echo "==> Instalando o CLI tcecode (via pipx)..."
# Prefere SSH (repo institucional privado); cai para HTTPS se não houver chave configurada.
if ssh -T git@bitbucket.org 2>&1 | grep -qi "authenticated\|logged in"; then
  pipx install "$REPO_SSH"
else
  echo "Aviso: SSH para bitbucket.org não configurado — tentando HTTPS (pode pedir usuário/senha ou app password)."
  pipx install "$REPO_HTTPS"
fi

hash -r

echo "==> Instalando o engine (tcecode-agent)..."
if ! tcecode update; then
  echo ""
  echo "Não foi possível baixar o engine automaticamente."
  echo "Se o repositório for privado, configure um ~/.netrc com suas credenciais"
  echo "do Bitbucket (usuário + App Password) e rode: tcecode update"
  exit 1
fi

echo ""
echo "==> tcecode instalado! Rode 'tcecode login' para autenticar e 'tcecode configure' para configurar sua squad."
