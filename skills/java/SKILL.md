# Skill: Java Institucional

## Quando usar

- Todo backend novo deve usar Java LTS (versão aprovada pelo time de plataforma)
- Preferir records para DTOs e value objects
- Usar Optional corretamente — sem `.get()` sem verificação

## Padrões obrigatórios

- **Sem lógica de negócio em controllers** — controllers apenas delegam
- **Sem acesso a repositório em controllers** — usar casos de uso / services
- **Exceções de negócio tipadas** — sem throws genéricos de RuntimeException sem motivo
- **Logs estruturados** — usar `log.info("mensagem", Map.of("campo", valor))` ou equivalente
- **Nunca logar dados sensíveis** — sem CPF, senha, token, API key em logs

## Anti-patterns

- God classes (services com 1000+ linhas)
- Static utilities para lógica de negócio
- Dependências circulares entre packages
- Capturar Exception genérica sem re-throw ou tratamento real
- System.out.println em código de produção

## Segurança

- Validar entrada nos controllers com Bean Validation (`@Valid`)
- Nunca construir SQL por concatenação de strings
- Usar prepared statements / JPA / QueryDSL
- Sanitizar dados antes de logar

## Testes

- JUnit 5 + Mockito para unitários
- Testcontainers para integração com banco real
- ArchUnit para regras arquiteturais automatizadas

## Relacionamentos

- [[../spring-boot/SKILL.md]]
