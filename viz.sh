#!/usr/bin/env bash
# Gera viz.html do knowledge bundle tce-ai-platform

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$SCRIPT_DIR/knowledge"
VENV="$HOME/.claude/skills/okf/vendor/knowledge-catalog/okf/.venv"
BUNDLE_NAME="TCE AI Platform"

if [[ ! -d "$VENV" ]]; then
  echo "Erro: venv do reference_agent não encontrado em $VENV" >&2
  exit 1
fi

source "$VENV/bin/activate"

python -m reference_agent visualize \
  --bundle "$BUNDLE_DIR" \
  --name "$BUNDLE_NAME"

OUTPUT="$BUNDLE_DIR/viz.html"

if [[ -f "$OUTPUT" ]]; then
  echo "Gerado: $OUTPUT"
  # Abrir no browser se possível
  if command -v open &>/dev/null; then
    open "$OUTPUT"
  elif command -v xdg-open &>/dev/null; then
    xdg-open "$OUTPUT"
  fi
fi
