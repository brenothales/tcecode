---
id: logical-models
type: Architecture Pattern
title: Modelos Lógicos Institucionais
status: active
---

# Modelos Lógicos Institucionais

Os desenvolvedores nunca configuram diretamente modelos de provedores. Usam apenas os nomes lógicos abaixo. O AI Gateway traduz para o modelo real e pode trocar o provedor sem impacto no cliente.

## Mapeamento atual

| Modelo lógico | Provedor atual | Modelo real | Uso indicado |
|---|---|---|---|
| `institutional-coding` | Anthropic | `claude-3-5-sonnet-20241022` | Tarefa principal de coding — alta qualidade |
| `institutional-reasoning` | OpenAI | `o3` | Raciocínio complexo, arquitetura, debugging difícil |
| `institutional-fast` | Google | `gemini-2.0-flash` | Tarefas simples, autocompletion, respostas rápidas |
| `institutional-local` | Ollama (on-prem) | `qwen2.5-coder:32b` | Código sensível, air-gapped, sem saída de dados |

## Regras de uso por role

| Role | Modelos permitidos |
|---|---|
| `AI_DEVELOPER` | `institutional-coding`, `institutional-fast`, `institutional-local` |
| `AI_ARCHITECT` | todos |
| `AI_SQUAD_ADMIN` | todos |
| `AI_PLATFORM_ADMIN` | todos |

## Como o desenvolvedor seleciona o modelo

```bash
# Usar modelo padrão da squad (definido pelo AI_SQUAD_ADMIN)
tce-ai

# Usar modelo específico para a sessão
tce-ai --model institutional-reasoning

# Ver modelos disponíveis
tce-ai models
```

## Como trocar o provedor (sem impacto nos devs)

Editar `litellm-config.yaml` no repositório `tce-ai-gateway/`:

```yaml
# Antes:
- model_name: institutional-coding
  litellm_params:
    model: anthropic/claude-3-5-sonnet-20241022

# Depois (troca para GPT-4o sem alterar nada no cliente):
- model_name: institutional-coding
  litellm_params:
    model: openai/gpt-4o
```

Deploy do gateway — sem rebuild do CLI nem comunicação às squads.

## Relacionamentos

- [ai-gateway](/architecture/ai-gateway.md)
- [adr-003-ai-gateway](/decisions/adr-003-ai-gateway.md)
