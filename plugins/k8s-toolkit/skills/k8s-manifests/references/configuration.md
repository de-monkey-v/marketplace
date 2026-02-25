# Configuration 상세 가이드

ConfigMap, Secret, 환경변수 관리의 상세 패턴과 실전 YAML 예제를 제공합니다.

---

## ConfigMap

비민감 설정 데이터를 저장합니다.

### 생성 방법

**literal 값으로 생성 (kubectl):**
```bash
kubectl create configmap my-config \
  --from-literal=DATABASE_HOST=postgres \
  --from-literal=DATABASE_PORT=5432 \
  --from-literal=LOG_LEVEL=info \
  -n production
```

**파일에서 생성:**
```bash
kubectl create configmap app-config \
  --from-file=config.yaml \
  --from-file=app.properties \
  -n production
```

**env 파일에서 생성:**
```bash
kubectl create configmap env-config \
  --from-env-file=.env.production \
  -n production
```

### YAML로 직접 작성

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
  namespace: production
  labels:
    app.kubernetes.io/name: my-app
data:
  # 단순 키-값
  DATABASE_HOST: "postgresql.production.svc.cluster.local"
  DATABASE_PORT: "5432"
  LOG_LEVEL: "info"
  # 파일 내용 (멀티라인)
  app.yaml: |
    server:
      port: 8080
      timeout: 30s
    database:
      maxConnections: 10
  nginx.conf: |
    server {
      listen 80;
      location / {
        proxy_pass http://localhost:8080;
      }
    }
```

### 마운트 방법

**envFrom으로 전체 ConfigMap을 환경변수로 주입:**
```yaml
spec:
  containers:
    - name: app
      envFrom:
        - configMapRef:
            name: my-app-config
```

**env로 특정 키만 선택:**
```yaml
spec:
  containers:
    - name: app
      env:
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: my-app-config
              key: LOG_LEVEL
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: my-app-config
              key: DATABASE_HOST
              optional: true  # 키가 없어도 Pod 시작 허용
```

**볼륨으로 파일 마운트:**
```yaml
spec:
  volumes:
    - name: config
      configMap:
        name: my-app-config
        items:
          - key: app.yaml      # ConfigMap 키
            path: config.yaml  # 마운트 경로의 파일명
        defaultMode: 0644
  containers:
    - name: app
      volumeMounts:
        - name: config
          mountPath: /etc/config
          readOnly: true
```

파일 마운트 시 `/etc/config/config.yaml`로 접근 가능합니다.

### ConfigMap 자동 리로드 패턴

ConfigMap이 변경될 때 앱을 자동으로 재시작하거나 리로드합니다.

**Reloader 사용 (stakater/Reloader):**
```yaml
metadata:
  annotations:
    reloader.stakater.com/auto: "true"
    # 또는 특정 ConfigMap만 감시
    configmap.reloader.stakater.com/reload: "my-app-config"
```

**inotify를 사용한 파일 변경 감지 (sidecar 패턴):**
```yaml
spec:
  containers:
    - name: app
      # 앱 컨테이너
    - name: config-reloader
      image: jimmidyson/configmap-reload:v0.9.0
      args:
        - --volume-dir=/etc/config
        - --webhook-url=http://localhost:8080/-/reload
      volumeMounts:
        - name: config
          mountPath: /etc/config
```

---

## Secret

민감한 데이터를 저장합니다. ConfigMap과 동일한 방식으로 마운트하되, 민감 정보 취급에 주의합니다.

### Secret 유형

| 유형 | 설명 | 자동 생성 |
|------|------|-----------|
| `Opaque` | 범용 비밀 (기본값) | - |
| `kubernetes.io/tls` | TLS 인증서 | cert-manager |
| `kubernetes.io/dockerconfigjson` | 컨테이너 레지스트리 인증 | - |
| `kubernetes.io/basic-auth` | 기본 인증 | - |
| `kubernetes.io/ssh-auth` | SSH 키 | - |
| `kubernetes.io/service-account-token` | ServiceAccount 토큰 | 자동 |

### Opaque Secret 작성

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-app-secret
  namespace: production
  labels:
    app.kubernetes.io/name: my-app
type: Opaque
stringData:
  # stringData: 평문 입력, 자동으로 base64 인코딩
  DATABASE_PASSWORD: "<YOUR_DATABASE_PASSWORD>"
  API_KEY: "<YOUR_API_KEY>"
  JWT_SECRET: "<YOUR_JWT_SECRET>"
```

`stringData`를 사용하면 base64 인코딩 없이 평문으로 작성할 수 있습니다. `data` 필드는 base64 인코딩된 값을 사용합니다.

```yaml
# data 필드 사용 시 (base64 인코딩 필요)
data:
  DATABASE_PASSWORD: czNjdXIzLXBAc3N3MHJk  # echo -n "<YOUR_DATABASE_PASSWORD>" | base64
```

### TLS Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-tls-secret
  namespace: production
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-cert>
  tls.key: <base64-encoded-key>
```

kubectl로 생성:
```bash
kubectl create secret tls my-tls-secret \
  --cert=server.crt \
  --key=server.key \
  -n production
```

### Docker Registry Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: registry-credentials
  namespace: production
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <base64-encoded-docker-config>
```

kubectl로 생성:
```bash
kubectl create secret docker-registry registry-credentials \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=password \
  --docker-email=user@example.com \
  -n production
```

Pod에서 사용:
```yaml
spec:
  imagePullSecrets:
    - name: registry-credentials
```

### Secret 마운트

**envFrom으로 전체 Secret을 환경변수로 주입:**
```yaml
spec:
  containers:
    - name: app
      envFrom:
        - secretRef:
            name: my-app-secret
```

**볼륨으로 파일 마운트 (권장):**
```yaml
spec:
  volumes:
    - name: secrets
      secret:
        secretName: my-app-secret
        defaultMode: 0400  # 읽기 전용 (소유자만)
  containers:
    - name: app
      volumeMounts:
        - name: secrets
          mountPath: /etc/secrets
          readOnly: true
```

환경변수보다 파일 마운트가 더 안전합니다. 환경변수는 자식 프로세스에 노출될 수 있습니다.

---

## 환경변수 주입 패턴

### envFrom vs env

```yaml
spec:
  containers:
    - name: app
      # 방법 1: ConfigMap 전체 주입
      envFrom:
        - configMapRef:
            name: my-app-config
        - secretRef:
            name: my-app-secret
            optional: false  # Secret이 없으면 Pod 시작 실패
      # 방법 2: 특정 키만 선택
      env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: my-app-secret
              key: DATABASE_URL
```

### Downward API (Pod 메타데이터 주입)

Pod 자신의 메타데이터를 환경변수 또는 파일로 주입합니다.

**환경변수로 주입:**
```yaml
env:
  - name: POD_NAME
    valueFrom:
      fieldRef:
        fieldPath: metadata.name
  - name: POD_NAMESPACE
    valueFrom:
      fieldRef:
        fieldPath: metadata.namespace
  - name: POD_IP
    valueFrom:
      fieldRef:
        fieldPath: status.podIP
  - name: NODE_NAME
    valueFrom:
      fieldRef:
        fieldPath: spec.nodeName
  - name: CPU_REQUEST
    valueFrom:
      resourceFieldRef:
        containerName: app
        resource: requests.cpu
  - name: MEMORY_LIMIT
    valueFrom:
      resourceFieldRef:
        containerName: app
        resource: limits.memory
```

**볼륨으로 주입:**
```yaml
spec:
  volumes:
    - name: pod-info
      downwardAPI:
        items:
          - path: "labels"
            fieldRef:
              fieldPath: metadata.labels
          - path: "annotations"
            fieldRef:
              fieldPath: metadata.annotations
  containers:
    - name: app
      volumeMounts:
        - name: pod-info
          mountPath: /etc/pod-info
```

---

## 민감정보 관리 패턴

Git에 Secret을 직접 커밋하지 않는 방법들입니다.

### External Secrets Operator

외부 시크릿 저장소(AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault 등)에서 Secret을 동기화합니다.

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-app-secret
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager   # SecretStore 이름
    kind: ClusterSecretStore
  target:
    name: my-app-secret        # 생성될 Kubernetes Secret 이름
    creationPolicy: Owner
  data:
    - secretKey: DATABASE_PASSWORD
      remoteRef:
        key: production/my-app   # AWS Secrets Manager 경로
        property: database_password
  dataFrom:
    - extract:
        key: production/my-app   # 전체 JSON 키-값 추출
```

### Sealed Secrets

암호화된 Secret을 Git에 안전하게 저장합니다.

```bash
# 평문 Secret을 SealedSecret으로 암호화
kubeseal --format=yaml < secret.yaml > sealed-secret.yaml

# SealedSecret은 Git에 커밋 가능
git add sealed-secret.yaml
```

```yaml
# sealed-secret.yaml (Git에 커밋 가능)
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: my-app-secret
  namespace: production
spec:
  encryptedData:
    DATABASE_PASSWORD: AgBy3...  # 암호화된 값
```

### HashiCorp Vault 연동

**Vault Agent Injector 사용:**
```yaml
metadata:
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "my-app"
    vault.hashicorp.com/agent-inject-secret-config: "secret/data/my-app/config"
    vault.hashicorp.com/agent-inject-template-config: |
      {{- with secret "secret/data/my-app/config" -}}
      DATABASE_PASSWORD={{ .Data.data.database_password }}
      API_KEY={{ .Data.data.api_key }}
      {{- end }}
```

---

## 환경별 설정 관리 전략

### Kustomize 사용

```
base/
├── configmap.yaml
└── kustomization.yaml

overlays/
├── development/
│   ├── configmap-patch.yaml
│   └── kustomization.yaml
└── production/
    ├── configmap-patch.yaml
    └── kustomization.yaml
```

```yaml
# overlays/production/configmap-patch.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
data:
  LOG_LEVEL: "warn"
  DATABASE_POOL_SIZE: "20"
```

### Helm Values 사용

```yaml
# values.yaml
config:
  logLevel: info
  databasePoolSize: 5

# values-production.yaml
config:
  logLevel: warn
  databasePoolSize: 20
```

```yaml
# templates/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "my-app.fullname" . }}-config
data:
  LOG_LEVEL: {{ .Values.config.logLevel | quote }}
  DATABASE_POOL_SIZE: {{ .Values.config.databasePoolSize | quote }}
```
