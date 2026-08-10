# Skill: Kubernetes Institucional

## Checklist obrigatório para todo Deployment

```yaml
spec:
  template:
    spec:
      # Nunca rodar como root
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000

      containers:
        - name: app
          # Sempre declarar requests e limits
          resources:
            requests:
              cpu: "100m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"

          # Probes obrigatórios
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10

          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 5

          # Secrets via env — nunca hardcoded
          env:
            - name: DATABASE_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: <servico>-secrets
                  key: database-password

          # Container sem privilégios
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
```

## Secrets — regras

- **Nunca** valores reais em arquivos versionados
- Kubernetes Secrets: para Fase 1
- Vault Agent Sidecar: para Fase 6 (rotação automática)
- Secrets de infra ficam no namespace da plataforma, nunca nos namespaces das squads

## Namespaces sugeridos

```
ai-platform        ← gateway, keycloak, observabilidade
squad-<nome>       ← serviços de cada squad
monitoring         ← prometheus, grafana, loki
```

## HPA mínimo para serviços de produção

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

## NetworkPolicy — princípio do menor privilégio

```yaml
# Default deny-all no namespace, depois adicionar allows específicos
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

## Anti-patterns Kubernetes

- `image: latest` — sempre usar tag específica
- Sem resource limits — pod pode consumir todo o nó
- Sem probes — pod recebe tráfego antes de estar pronto
- Secrets em ConfigMap — ConfigMap não é secret
- `privileged: true` sem justificativa

## Relacionamentos

- [[../spring-boot/SKILL.md]]
