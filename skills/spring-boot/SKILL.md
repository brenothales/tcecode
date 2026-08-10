# Skill: Spring Boot Institucional

## Estrutura de pacotes padrão (Hexagonal)

```
com.tce.<servico>/
  application/
    usecase/          ← casos de uso (regras de negócio)
    port/
      in/             ← interfaces de entrada (UseCasePort)
      out/            ← interfaces de saída (RepositoryPort, GatewayPort)
  domain/
    model/            ← entidades e value objects
    exception/        ← exceções de domínio
  infrastructure/
    adapter/
      in/
        web/          ← controllers REST
        messaging/    ← consumers Kafka
      out/
        persistence/  ← repositórios JPA
        http/         ← clientes HTTP externos
    config/           ← configurações Spring
```

## Obrigatório em todo serviço

- **Actuator:** `/actuator/health`, `/actuator/info`, `/actuator/prometheus`
- **OpenAPI:** `springdoc-openapi` configurado, swagger-ui disponível em `/swagger-ui.html`
- **Observabilidade:** Micrometer + OpenTelemetry para traces distribuídos
- **Logs JSON:** Logback com encoder JSON (Logstash ou estruturado)
- **Profiles:** `local`, `dev`, `prod` — nunca hardcodar configurações de ambiente

## application.yaml padrão

```yaml
spring:
  application:
    name: ${SERVICE_NAME:meu-servico}
  datasource:
    url: ${DATABASE_URL}
    username: ${DATABASE_USER}
    password: ${DATABASE_PASSWORD}

management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus
  tracing:
    sampling:
      probability: 1.0  # reduzir em produção com alto volume

logging:
  structured:
    format:
      console: ecs  # Elastic Common Schema
```

## Anti-patterns Spring

- `@Autowired` em campo — usar injeção por construtor
- `@Transactional` em controllers
- Business logic em `@Repository`
- `@SpringBootTest` para todo teste (usar slices: `@WebMvcTest`, `@DataJpaTest`)
- Properties hardcoded — sempre via `@ConfigurationProperties` ou `@Value("${...}")`

## Segurança Spring Security

- Habilitar CSRF para endpoints web (desabilitar apenas para APIs REST stateless)
- Usar `SecurityFilterChain` bean (não estender `WebSecurityConfigurerAdapter` — deprecated)
- JWT validation via Spring Security OAuth2 Resource Server
- Nunca retornar stack trace completo em respostas de erro

## Testes

```java
// Unitário — sem Spring context
@ExtendWith(MockitoExtension.class)
class MeuUseCaseTest { }

// Integração com banco real
@SpringBootTest
@Testcontainers
class MeuRepositoryIntegrationTest { }

// Slice de controller
@WebMvcTest(MeuController.class)
class MeuControllerTest { }
```

## Relacionamentos

- [[../java/SKILL.md]]
- [[../kubernetes/SKILL.md]]
