---
name: k8s-manifests
description: "This skill should be used when the user asks to \"deployment 작성\", \"service 만들어\", \"ingress 설정\", \"매니페스트\", \"yaml 작성\", \"k8s 리소스\", \"configmap\", \"secret\", \"pvc\", \"rbac\", \"k8s manifest\", \"kubernetes yaml\", or mentions writing Kubernetes resource manifests. Provides best practices for Kubernetes manifest authoring."
version: 0.1.0
---

# Kubernetes 매니페스트 작성 가이드

Kubernetes 리소스 매니페스트를 작성할 때 따라야 할 공통 원칙과 각 리소스 유형별 핵심 체크포인트를 제공합니다.

## 공통 원칙

### 라벨링 컨벤션 (app.kubernetes.io/*)

모든 리소스에 표준 라벨을 일관되게 적용합니다.

```yaml
metadata:
  labels:
    app.kubernetes.io/name: my-app          # 앱 이름
    app.kubernetes.io/instance: my-app-prod # 앱 인스턴스 (릴리즈명)
    app.kubernetes.io/version: "1.0.0"      # 앱 버전
    app.kubernetes.io/component: backend    # 컴포넌트 역할
    app.kubernetes.io/part-of: my-platform  # 상위 플랫폼
    app.kubernetes.io/managed-by: helm      # 관리 도구
```

추가 운영용 어노테이션 예시:

```yaml
metadata:
  annotations:
    team: "platform-team"
    contact: "infra@example.com"
    description: "API 서버 Deployment"
```

### 네임스페이스 전략

- **production / staging / development** 환경별 네임스페이스를 분리합니다.
- 모든 매니페스트에 `namespace` 필드를 명시합니다 (default 네임스페이스 사용 금지).
- `ResourceQuota`와 `LimitRange`를 네임스페이스마다 설정합니다.

```yaml
metadata:
  namespace: production
```

---

## 리소스 유형별 핵심 체크포인트

### Workloads (Deployment, StatefulSet, DaemonSet, Job, CronJob)

| 체크포인트 | 설명 |
|-----------|------|
| `replicas` | 가용성 요구에 맞는 복제 수 설정 |
| `strategy` | RollingUpdate vs Recreate 선택 |
| `selector.matchLabels` | `template.metadata.labels`와 일치 여부 확인 |
| `resources` | requests/limits 반드시 설정 |
| `probes` | liveness/readiness/startup probe 구성 |
| `securityContext` | runAsNonRoot, readOnlyRootFilesystem 설정 |
| `affinity` | 고가용성을 위한 안티어피니티 설정 |

상세 패턴은 [`references/workloads.md`](references/workloads.md) 참조.

### Networking (Service, Ingress, NetworkPolicy)

| 체크포인트 | 설명 |
|-----------|------|
| `selector` | Service selector가 Pod 라벨과 일치하는지 확인 |
| `port` / `targetPort` | 서비스 포트와 컨테이너 포트 매핑 확인 |
| `ingressClassName` | Ingress 컨트롤러 명시 |
| `tls` | HTTPS 인증서 설정 여부 |
| NetworkPolicy | 기본 거부 정책 + 필요한 트래픽만 허용 |

상세 패턴은 [`references/networking.md`](references/networking.md) 참조.

### Configuration (ConfigMap, Secret)

| 체크포인트 | 설명 |
|-----------|------|
| ConfigMap | 환경별 값 분리, 마운트 vs envFrom 선택 |
| Secret | 민감 정보 base64 인코딩, external-secrets 연동 권장 |
| 환경변수 | downward API로 Pod 메타데이터 주입 가능 |

상세 패턴은 [`references/configuration.md`](references/configuration.md) 참조.

### Storage (PV, PVC, StorageClass)

| 체크포인트 | 설명 |
|-----------|------|
| `accessModes` | RWO / ROX / RWX 요구에 맞게 선택 |
| `storageClassName` | 적절한 StorageClass 지정 |
| `reclaimPolicy` | Retain vs Delete (데이터 보존 필요 시 Retain) |
| `volumeClaimTemplates` | StatefulSet에서 사용 |

상세 패턴은 [`references/storage.md`](references/storage.md) 참조.

### RBAC (Role, ClusterRole, ServiceAccount)

| 체크포인트 | 설명 |
|-----------|------|
| 최소 권한 원칙 | 꼭 필요한 리소스와 verbs만 부여 |
| 네임스페이스 범위 우선 | ClusterRole보다 Role 우선 사용 |
| ServiceAccount | `automountServiceAccountToken: false` 기본값 권장 |
| Pod Security | Baseline 이상 적용 권장 |

상세 패턴은 [`references/rbac.md`](references/rbac.md) 참조.

### Scaling & 리소스 관리 (HPA, VPA, ResourceQuota, LimitRange)

| 체크포인트 | 설명 |
|-----------|------|
| HPA | CPU/메모리 기준 자동 스케일링, minReplicas 최소 2 |
| VPA | 개발 환경에서 권장값 수집 후 적용 |
| ResourceQuota | 네임스페이스별 리소스 총량 제한 |
| LimitRange | 컨테이너 기본값 및 최대값 제한 |

상세 패턴은 [`references/hpa-resources.md`](references/hpa-resources.md) 참조.

---

## 보안 기본 설정

모든 컨테이너에 securityContext를 명시합니다.

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
```

**필수 체크:**
- `runAsNonRoot: true` - root 실행 금지
- `readOnlyRootFilesystem: true` - 파일시스템 읽기 전용
- `allowPrivilegeEscalation: false` - 권한 상승 금지
- `capabilities.drop: [ALL]` - 모든 리눅스 기능 제거

---

## 리소스 제한 설정 원칙

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

**원칙:**
- `requests`는 실제 평균 사용량 기준으로 설정합니다.
- `limits`는 requests의 2~4배 이내로 설정합니다 (OOMKilled 방지).
- CPU limits는 throttling을 유발할 수 있으므로 신중하게 설정합니다.
- memory limits는 반드시 설정합니다 (미설정 시 노드 자원 고갈 위험).
- QoS 클래스 목표: 중요 서비스는 **Guaranteed** (requests == limits) 권장.

---

## 프로브 설정 기준

| 프로브 | 목적 | 사용 시기 |
|--------|------|-----------|
| `livenessProbe` | 컨테이너 재시작 트리거 | 데드락 감지, 무한 루프 방지 |
| `readinessProbe` | 트래픽 수신 가능 여부 | 초기화 완료 후 트래픽 허용 |
| `startupProbe` | 느린 시작 앱 처리 | 초기화가 오래 걸리는 앱 |

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3

startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
```

**체크포인트:**
- `startupProbe`는 초기화가 30초 이상 걸리는 앱에 필수입니다.
- `livenessProbe`의 `failureThreshold`를 너무 낮게 설정하면 불필요한 재시작이 발생합니다.
- `readinessProbe`는 트래픽을 받을 준비가 됐을 때만 통과하도록 엔드포인트를 구현합니다.

---

## 안티어피니티 기본 패턴

고가용성을 위해 동일 앱의 Pod가 여러 노드에 분산되도록 설정합니다.

```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: my-app
          topologyKey: kubernetes.io/hostname
```

`required` 대신 `preferred`를 사용하면 노드가 부족할 때도 스케줄링이 가능합니다.

---

## 참고 자료

### Reference Files

- **[`references/workloads.md`](references/workloads.md)** - Deployment, StatefulSet, DaemonSet, Job, CronJob 상세 패턴
- **[`references/networking.md`](references/networking.md)** - Service, Ingress, NetworkPolicy 상세 가이드
- **[`references/configuration.md`](references/configuration.md)** - ConfigMap, Secret, 환경변수 관리
- **[`references/storage.md`](references/storage.md)** - PV, PVC, StorageClass 상세 가이드
- **[`references/rbac.md`](references/rbac.md)** - Role, ClusterRole, ServiceAccount 패턴
- **[`references/hpa-resources.md`](references/hpa-resources.md)** - HPA, VPA, ResourceQuota, LimitRange
