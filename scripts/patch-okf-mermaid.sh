#!/usr/bin/env bash
# Aplica suporte a Mermaid no viewer da skill OKF.
# Executar uma vez por máquina após instalar/atualizar a skill OKF.
#
# Uso: bash scripts/patch-okf-mermaid.sh

set -euo pipefail

VENDOR="$HOME/.claude/skills/okf/vendor/knowledge-catalog/okf/src/reference_agent/viewer"
TEMPLATE="$VENDOR/templates/viz.html"
VIZ_JS="$VENDOR/static/viz.js"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "Erro: template não encontrado em $TEMPLATE" >&2
  echo "Instale a skill OKF primeiro." >&2
  exit 1
fi

# ----- 1. Adicionar script Mermaid ao template HTML -----
if grep -q "mermaid" "$TEMPLATE"; then
  echo "✓ Template já tem Mermaid — pulando."
else
  sed -i '' \
    's|<script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js"></script>|<script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js"></script>\n<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>|' \
    "$TEMPLATE"
  echo "✓ Script Mermaid adicionado ao template."
fi

# ----- 2. Adicionar renderização Mermaid ao viz.js -----
if grep -q "mermaid" "$VIZ_JS"; then
  echo "✓ viz.js já tem Mermaid — pulando."
else
  # Insere o bloco após a linha que contém rewriteInternalLinks(bodyEl)
  python3 - "$VIZ_JS" <<'PYEOF'
import sys, pathlib

path = pathlib.Path(sys.argv[1])
src = path.read_text()

anchor = "    rewriteInternalLinks(bodyEl);"
insert = """    // render mermaid diagrams inside the detail panel
    bodyEl.querySelectorAll("pre code.language-mermaid").forEach((el) => {
      const src = el.textContent || "";
      const wrapper = document.createElement("div");
      wrapper.className = "mermaid";
      wrapper.textContent = src;
      el.parentElement.replaceWith(wrapper);
    });
    if (bodyEl.querySelector(".mermaid")) {
      const theme = document.documentElement.dataset.theme === "dark" ? "dark" : "default";
      mermaid.initialize({ startOnLoad: false, theme });
      mermaid.run({ nodes: bodyEl.querySelectorAll(".mermaid") });
    }"""

if anchor not in src:
    print("Erro: âncora não encontrada em viz.js — a versão do vendor pode ter mudado.")
    sys.exit(1)

patched = src.replace(anchor, anchor + "\n" + insert, 1)
path.write_text(patched)
print("✓ Renderização Mermaid adicionada ao viz.js.")
PYEOF
fi

echo ""
echo "Patch aplicado. Regenere o viz.html com: ./viz.sh"
