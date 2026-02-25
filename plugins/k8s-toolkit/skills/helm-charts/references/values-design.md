# values.yaml 설계 패턴

values.yaml은 차트의 기본 설정을 정의하는 핵심 파일입니다. 올바른 설계는 차트의 유연성과 사용성을 결정합니다.

## 구조 설계 원칙

### 최상위 키 네이밍

최상위 키는 기능 그룹을 기준으로 명명합니다:

```yaml
# 권장: 기능 그룹별 최상위 키
image:          # 이미지 설정
replicaCount:   # 복제본 수
service:        # 서비스 설정
ingress:        # 인그레스 설정
resources:      # 리소스 제한
autoscaling:    # 오토스케일링
serviceAccount: # 서비스 계정
podAnnotations: # Pod 어노테이션
nodeSelector:   # 노드 셀렉터
tolerations:    # 테인트 허용
affinity:       # 어피니티 설정
```

### 중첩 레벨 가이드

3단계 이상 중첩은 가독성을 해치므로 지양합니다:

```yaml
# 좋음: 2단계 중첩
database:
  host: localhost
  port: 5432
  name: mydb

# 나쁨: 과도한 중첩 (4단계)
database:
  connection:
    primary:
      host: localhost  # 너무 깊음
```

### 완전한 values.yaml 예시

```yaml
# 기본값은 개발 환경 기준으로 설정
replicaCount: 1

image:
  repository: my-registry/my-app
  pullPolicy: IfNotPresent
  # 명시적 태그 설정 (latest 사용 금지)
  tag: ""  # Chart.yaml appVersion을 기본값으로 사용

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations: {}
podLabels: {}

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000

securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL

service:
  type: ClusterIP
  port: 80
  targetPort: 8080
  # 선택적: NodePort 설정
  # nodePort: 30080

ingress:
  enabled: false
  className: ""
  annotations: {}
    # kubernetes.io/ingress.class: nginx
    # cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: Prefix
  tls: []
  # - secretName: chart-example-tls
  #   hosts:
  #     - chart-example.local

resources:
  # 프로덕션에서는 반드시 설정
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi

livenessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  # targetMemoryUtilizationPercentage: 80

# 추가 볼륨
volumes: []
volumeMounts: []

nodeSelector: {}
tolerations: []
affinity: {}

# 애플리케이션별 설정
config:
  logLevel: info
  port: 8080

# 외부 서비스 연결
database:
  host: ""
  port: 5432
  name: myapp
  existingSecret: ""    # Secret 이름 (비밀값은 Secret으로)
  secretKey: password   # Secret 내 키 이름
```

## 환경별 분리

### 파일 구조

```
my-app/
├── values.yaml           # 기본값 (개발 환경)
├── values-dev.yaml       # 개발 환경 오버라이드
├── values-staging.yaml   # 스테이징 환경 오버라이드
└── values-prod.yaml      # 프로덕션 환경 오버라이드
```

**values-dev.yaml:**

```yaml
# 개발 환경: 최소 리소스, 디버그 모드
replicaCount: 1

image:
  tag: "dev-latest"

config:
  logLevel: debug

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 50m
    memory: 64Mi

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: my-app.dev.example.com
      paths:
        - path: /
          pathType: Prefix
```

**values-prod.yaml:**

```yaml
# 프로덕션 환경: 고가용성, 엄격한 보안
replicaCount: 3

image:
  tag: "1.2.3"    # 고정 태그 사용

config:
  logLevel: warn

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: my-app.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: my-app-tls
      hosts:
        - my-app.example.com

podDisruptionBudget:
  enabled: true
  minAvailable: 2
```

**배포 시 환경 values 적용:**

```bash
# 개발 환경
helm upgrade --install my-app ./my-app \
  --values values.yaml \
  --values values-dev.yaml \
  --namespace dev

# 프로덕션 환경 (--set으로 이미지 태그 동적 지정)
helm upgrade --install my-app ./my-app \
  --values values.yaml \
  --values values-prod.yaml \
  --set image.tag=$CI_COMMIT_TAG \
  --namespace prod
```

## JSON Schema 검증

`values.schema.json`으로 values.yaml 입력값을 강타입으로 검증합니다.

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "title": "Values",
  "type": "object",
  "required": ["image", "service"],
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "description": "Number of replicas"
    },
    "image": {
      "type": "object",
      "required": ["repository"],
      "properties": {
        "repository": {
          "type": "string",
          "minLength": 1
        },
        "tag": {
          "type": "string"
        },
        "pullPolicy": {
          "type": "string",
          "enum": ["Always", "IfNotPresent", "Never"]
        }
      }
    },
    "service": {
      "type": "object",
      "required": ["type", "port"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["ClusterIP", "NodePort", "LoadBalancer"]
        },
        "port": {
          "type": "integer",
          "minimum": 1,
          "maximum": 65535
        }
      }
    },
    "resources": {
      "type": "object",
      "properties": {
        "limits": {
          "type": "object",
          "properties": {
            "cpu": { "type": "string" },
            "memory": { "type": "string" }
          }
        },
        "requests": {
          "type": "object",
          "properties": {
            "cpu": { "type": "string" },
            "memory": { "type": "string" }
          }
        }
      }
    }
  }
}
```

검증 실행:

```bash
# helm lint 실행 시 자동으로 JSON Schema 검증
helm lint ./my-app --values values-prod.yaml
```

## 기본값 설정 원칙

**개발 환경 기본, 프로덕션 오버라이드 패턴:**

```yaml
# values.yaml: 개발자가 바로 실행 가능한 기본값
replicaCount: 1      # 개발용 최소값
resources:
  limits:
    cpu: 200m        # 개발용 낮은 제한
    memory: 256Mi
```

**필수값 강제 (`required` 함수):**

```yaml
# templates/deployment.yaml
- name: DB_HOST
  value: {{ required "database.host is required" .Values.database.host | quote }}
```

**`default` 함수로 안전한 기본값:**

```yaml
image:
  tag: {{ .Values.image.tag | default .Chart.AppVersion }}
```

## 글로벌 값 활용

`global` 키는 서브차트 전체에 공유됩니다:

```yaml
# 부모 차트 values.yaml
global:
  imageRegistry: my-registry.example.com
  imagePullSecrets:
    - name: my-registry-secret
  storageClass: standard

# 서브차트에서 접근
# {{ .Values.global.imageRegistry }}
```

```yaml
# subchart values.yaml (global 병합)
image:
  registry: "{{ .Values.global.imageRegistry | default \"docker.io\" }}"
  repository: my-subchart
```

## 타입 안전 주의사항

YAML 파싱 시 타입이 의도치 않게 변환될 수 있습니다:

```yaml
# 주의 필요한 값들
version: 1.10       # float로 파싱됨 → "1.10"으로 인식됨
tag: "1.10"         # 명시적 문자열 사용 권장
port: 8080          # 정수 OK
enabled: true       # bool OK

# 환경변수 값은 항상 문자열로
env:
  - name: PORT
    value: "8080"   # 문자열로 명시 (숫자 아님)
  - name: DEBUG
    value: "false"  # 문자열로 명시 (bool 아님)
```

템플릿에서 `quote` 파이프라인으로 타입 안전 보장:

```yaml
env:
  - name: PORT
    value: {{ .Values.service.port | quote }}
  - name: LOG_LEVEL
    value: {{ .Values.config.logLevel | quote }}
```
