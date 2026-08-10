#!/usr/bin/env bash
# Aplica patches no viewer/gerador da skill OKF: suporte a Mermaid +
# fix de escaping que evita quebra da página quando um concept contém
# um literal `</script>` no corpo (ex.: exemplos de código deste próprio runbook).
# Executar uma vez por máquina após instalar/atualizar a skill OKF.
#
# Uso: bash scripts/patch-okf-mermaid.sh

set -euo pipefail

VENDOR="$HOME/.claude/skills/okf/vendor/knowledge-catalog/okf/src/reference_agent/viewer"
TEMPLATE="$VENDOR/templates/viz.html"
VIZ_JS="$VENDOR/static/viz.js"
GENERATOR="$VENDOR/generator.py"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "Erro: template não encontrado em $TEMPLATE" >&2
  echo "Instale a skill OKF primeiro." >&2
  exit 1
fi

# ----- 1. Adicionar script Mermaid ao template HTML -----
# (usa python3 em vez de `sed -i ''` para funcionar em GNU sed e BSD sed)
if grep -q "mermaid" "$TEMPLATE"; then
  echo "✓ Template já tem Mermaid — pulando."
else
  python3 - "$TEMPLATE" <<'PYEOF'
import sys, pathlib

path = pathlib.Path(sys.argv[1])
src = path.read_text()

anchor = '<script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js"></script>'
insert = '<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>'

if anchor not in src:
    print("Erro: âncora não encontrada no template — a versão do vendor pode ter mudado.")
    sys.exit(1)

patched = src.replace(anchor, anchor + "\n" + insert, 1)
path.write_text(patched)
print("✓ Script Mermaid adicionado ao template.")
PYEOF
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

# ----- 3. Escapar "</" no JSON embutido do bundle (evita fechamento -----
# ----- prematuro da tag <script> quando um concept contém `</script>`) -----
if [[ ! -f "$GENERATOR" ]]; then
  echo "Aviso: generator.py não encontrado em $GENERATOR — pulando fix de escaping." >&2
elif grep -q '\.replace("</", "<\\\\/")' "$GENERATOR"; then
  echo "✓ generator.py já tem o fix de escaping — pulando."
else
  python3 - "$GENERATOR" <<'PYEOF'
import sys, pathlib

path = pathlib.Path(sys.argv[1])
src = path.read_text()

anchor = (
    '        .replace("__BUNDLE_NAME__", json.dumps(name))\n'
    '        .replace("__BUNDLE_DATA__", json.dumps(graph, default=str))'
)
replacement = (
    '        .replace("__BUNDLE_NAME__", json.dumps(name).replace("</", "<\\\\/"))\n'
    '        .replace("__BUNDLE_DATA__", json.dumps(graph, default=str).replace("</", "<\\\\/"))'
)

if anchor not in src:
    print("Erro: âncora não encontrada em generator.py — a versão do vendor pode ter mudado.")
    sys.exit(1)

patched = src.replace(anchor, replacement, 1)
path.write_text(patched)
print("✓ Fix de escaping aplicado ao generator.py.")
PYEOF
fi

echo ""
echo "Patch aplicado. Regenere o viz.html com: ./viz.sh"
