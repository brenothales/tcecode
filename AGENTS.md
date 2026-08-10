# AGENTS.md — Institutional AI Engineering Platform

Este arquivo define as regras institucionais para o agente de IA neste repositório.
**Leia este arquivo antes de qualquer modificação.**

---

## Identidade do projeto

- **Repositório:** `tce-ai-platform` (meta-repo / plataforma)
- **Stack:** Python 3.11+, Typer, LiteLLM, YAML, Docker, Kubernetes
- **Owner:** Equipe de Plataforma de IA

---

## Antes de implementar qualquer alteração

1. Ler `knowledge/index.md`
2. Identificar documentos de conhecimento relevantes para a tarefa
3. Ler decisões arquiteturais relacionadas (`knowledge/decisions/`)
4. Verificar se a alteração contradiz alguma decisão existente
5. Para tarefas complexas: apresentar plano antes de implementar

---

## O que NUNCA fazer

- Commitar API keys, secrets, passwords ou tokens reais
- Alterar o `litellm-config.yaml` para incluir secrets (use variáveis de ambiente)
- Criar dependências de provedores de IA específicos no código do CLI
- Remover mecanismos de segurança ou autenticação
- Fazer deploy em produção sem autorização explícita
- Ignorar testes existentes

---

## Stack e convenções

### Python (CLI)
- Python 3.11+ obrigatório
- Typer para comandos CLI
- Rich para output formatado
- Type hints obrigatórios
- Sem lógica de negócio em `main.py` — extrair para módulos específicos
- Testes com pytest

### Configuração
- Secrets: **sempre** via variáveis de ambiente ou Kubernetes Secrets
- Config do usuário: `~/.tce-ai/config.json` (chmod 600)
- Config do OpenCode: `~/.opencode/config.json` (chmod 600)
- Nunca logar secrets, tokens ou API keys

### Arquivos de configuração
- `litellm-config.yaml`: sem secrets — apenas `os.environ/NOME_VAR`
- `.env.example`: template sem valores reais
- `.env`: nunca commitar (está no .gitignore)

---

## Comandos úteis

```bash
# Instalar CLI em modo desenvolvimento
pip install -e cli/

# Executar o CLI
tce-ai --help

# Subir o gateway localmente
cd gateway && cp .env.example .env  # preencher .env
docker compose up -d

# Verificar status
tce-ai status
```

---

## Fluxo de trabalho do agente

```
1. Understand → ler knowledge/index.md e decisões relevantes
2. Inspect    → analisar arquivos afetados
3. Plan       → apresentar plano (para mudanças não triviais)
4. Implement  → código seguindo convenções acima
5. Test       → rodar testes, verificar que não quebraram
6. Review     → verificar quality gate (knowledge/reference/quality-gate.md)
7. OKF        → atualizar knowledge/ se decisão/padrão novo foi estabelecido
8. Git diff   → revisar antes de commit
```

---

## Quality gate rápido

- [ ] Nenhum secret no código ou config versionado
- [ ] Testes passam
- [ ] Type hints presentes
- [ ] `knowledge/` atualizado se decisão nova foi tomada
