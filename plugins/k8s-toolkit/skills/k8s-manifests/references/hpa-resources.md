# HPA, VPA, ResourceQuota, LimitRange 가이드

자동 스케일링과 리소스 관리의 상세 패턴과 실전 YAML 예제를 제공합니다.

---

## QoS 클래스 이해

Kubernetes는 requests/limits 설정에 따라 Pod에 QoS 클래스를 자동 부여합니다.

| QoS 클래스 | 조건 | OOM Kill 우선순위 |
|-----------|------|-----------------|
| `Guaranteed` | 모든 컨테이너의 cpu/memory requests == limits | 가장 낮음 (마지막에 종료) |
| `Burstable` | 일부 컨테이너에 requests 또는 limits 설정 | 중간 |
| `BestEffort` | requests/limits 미설정 | 가장 높음 (가장 먼저 종료) |

**권장:**
- 중요 서비스: `Guaranteed` (requests == limits)
- 일반 서비스: `Burstable` (requests < limits)
- 개발/테스트: `Burstable` 허용

```bash
# Pod의 QoS 클래스 확인
kubectl get pod my-pod -o jsonpath='{.status.qosClass}'
```

---

## requests/limits 설정 가이드

### 기본 원칙

```yaml
resources:
  requests:
    cpu: "100m"      # 평균 사용량 기준
    memory: "128Mi"  # 평균 사용량 기준
  limits:
    cpu: "500m"      # requests의 2~5배
    memory: "512Mi"  # requests의 2~4배 (OOMKilled 방지)
```

**CPU requests/limits 특성:**
- CPU는 압축 가능한 리소스입니다. limits 초과 시 throttling만 발생합니다.
- CPU limits를 너무 낮게 설정하면 성능 저하가 발생합니다.
- CPU requests는 스케줄링 결정에 사용됩니다.
- Java 앱은 JVM 힙 외에 추가 메모리(메타스페이스, 스택 등)를 고려해야 합니다.

**Memory requests/limits 특성:**
- Memory는 비압축 리소스입니다. limits 초과 시 OOMKilled 발생합니다.
- Memory limits는 반드시 설정합니다.
- OOMKilled 발생 시 limits 값을 확인하고 늘립니다.

```bash
# OOMKilled 확인
kubectl get pod my-pod -o jsonpath='{.status.containerStatuses[*].lastState.terminated.reason}'

# 리소스 사용량 확인
kubectl top pod my-pod
kubectl top pod my-pod --containers
```

### 초기 값 설정 전략

1. VPA Off 모드로 권장값 수집 (2주 이상)
2. 또는 부하 테스트 결과 기반으로 설정
3. p95 사용량을 requests, p99를 limits로 설정

---

## HPA (HorizontalPodAutoscaler)

CPU/메모리 사용률 또는 커스텀 메트릭 기반으로 Pod 수를 자동 조정합니다.

### CPU/메모리 기반 HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2      # 최소 2개 (고가용성 보장)
  maxReplicas: 20     # 최대 20개
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70  # 목표 CPU 사용률 (%)
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### 커스텀 메트릭 기반 HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 50
  metrics:
    # RPS 기반 스케일링
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"   # Pod당 RPS 목표
    # 외부 메트릭 (SQS 큐 깊이 등)
    - type: External
      external:
        metric:
          name: sqs_queue_depth
          selector:
            matchLabels:
              queue: my-app-queue
        target:
          type: Value
          value: "100"
```

### behavior (스케일링 동작 제어)

```yaml
spec:
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0    # 즉시 스케일 업 (0초 대기)
      policies:
        - type: Percent
          value: 100                    # 현재 Pod 수의 최대 100% 추가
          periodSeconds: 30
        - type: Pods
          value: 4                      # 최대 4개씩 추가
          periodSeconds: 30
      selectPolicy: Max                 # 더 큰 쪽 선택
    scaleDown:
      stabilizationWindowSeconds: 300  # 5분 대기 후 스케일 다운
      policies:
        - type: Percent
          value: 10                     # 현재 Pod 수의 최대 10% 제거
          periodSeconds: 60
        - type: Pods
          value: 2                      # 최대 2개씩 제거
          periodSeconds: 60
      selectPolicy: Min                 # 더 작은 쪽 선택 (보수적)
```

**stabilizationWindowSeconds:**
- 스케일 다운 시 300초(5분) 대기는 일시적 트래픽 감소에 의한 불필요한 스케일 다운을 방지합니다.
- 스케일 업 시 0초는 빠른 대응을 가능하게 합니다.

### HPA 상태 확인

```bash
kubectl get hpa my-app-hpa -n production
kubectl describe hpa my-app-hpa -n production

# KEDA (Kubernetes Event-Driven Autoscaling) 설치 시
kubectl get scaledobject -n production
```

---

## VPA (VerticalPodAutoscaler)

Pod의 CPU/메모리 requests/limits를 자동으로 조정합니다.

### VPA 설치 확인

```bash
kubectl get crd verticalpodautoscalers.autoscaling.k8s.io
```

### VPA 설정

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Off"      # Off / Initial / Recreate / Auto
  resourcePolicy:
    containerPolicies:
      - containerName: my-app
        minAllowed:
          cpu: "50m"
          memory: "64Mi"
        maxAllowed:
          cpu: "2"
          memory: "4Gi"
        controlledResources: ["cpu", "memory"]
        controlledValues: RequestsAndLimits  # RequestsOnly 또는 RequestsAndLimits
```

### updateMode 선택

| 모드 | 동작 | 권장 환경 |
|------|------|----------|
| `Off` | 권장값만 계산, 적용하지 않음 | 개발/분석 단계 |
| `Initial` | Pod 최초 생성 시에만 적용 | 안정적인 앱 |
| `Recreate` | 변경 시 Pod 재시작 | 재시작 허용 앱 |
| `Auto` | 자동으로 적용 방법 결정 | 실험적 |

**VPA와 HPA 동시 사용:**
- CPU/메모리 기반 HPA와 VPA를 동시에 사용하면 충돌이 발생합니다.
- HPA (CPU/메모리) + VPA를 같이 사용하려면 VPA를 `RequestsOnly`로 설정하거나, HPA는 커스텀 메트릭 기반으로 변경합니다.
- 권장: HPA(커스텀 메트릭) + VPA, 또는 HPA(CPU) 단독 사용.

### VPA 권장값 확인

```bash
kubectl describe vpa my-app-vpa -n production
```

출력에서 `Recommendation` 섹션을 확인합니다:
```
Recommendation:
  Container Recommendations:
    Container Name: my-app
    Lower Bound:
      Cpu:     50m
      Memory:  128Mi
    Target:
      Cpu:     200m
      Memory:  256Mi
    Upper Bound:
      Cpu:     1
      Memory:  1Gi
```

---

## ResourceQuota

네임스페이스의 리소스 총량을 제한합니다.

### 컴퓨트 리소스 쿼터

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
  namespace: production
spec:
  hard:
    # CPU/메모리 총량
    requests.cpu: "20"
    requests.memory: "40Gi"
    limits.cpu: "40"
    limits.memory: "80Gi"
    # GPU
    requests.nvidia.com/gpu: "4"
```

### 오브젝트 수 쿼터

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: object-counts
  namespace: production
spec:
  hard:
    pods: "50"
    services: "20"
    persistentvolumeclaims: "10"
    secrets: "20"
    configmaps: "20"
    replicationcontrollers: "0"   # RC 사용 금지
    # LoadBalancer 서비스 제한
    services.loadbalancers: "2"
    services.nodeports: "0"
```

### 우선순위 클래스 기반 쿼터

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: high-priority-quota
  namespace: production
spec:
  hard:
    pods: "10"
  scopeSelector:
    matchExpressions:
      - operator: In
        scopeName: PriorityClass
        values: ["high-priority"]
```

```bash
# 현재 사용량 확인
kubectl describe resourcequota -n production
```

---

## LimitRange

네임스페이스의 컨테이너/Pod/PVC별 기본값과 최대값을 설정합니다.

### 컨테이너 LimitRange

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: container-limits
  namespace: production
spec:
  limits:
    - type: Container
      default:              # limits 기본값 (미설정 시 적용)
        cpu: "500m"
        memory: "512Mi"
      defaultRequest:       # requests 기본값 (미설정 시 적용)
        cpu: "100m"
        memory: "128Mi"
      min:                  # 최솟값 제한
        cpu: "50m"
        memory: "64Mi"
      max:                  # 최댓값 제한
        cpu: "4"
        memory: "8Gi"
      maxLimitRequestRatio: # limits/requests 최대 비율
        cpu: "10"
        memory: "4"
```

### Pod LimitRange

```yaml
spec:
  limits:
    - type: Pod
      max:
        cpu: "8"
        memory: "16Gi"
      min:
        cpu: "100m"
        memory: "128Mi"
```

### PVC LimitRange

```yaml
spec:
  limits:
    - type: PersistentVolumeClaim
      max:
        storage: 100Gi
      min:
        storage: 1Gi
```

```bash
# LimitRange 확인
kubectl describe limitrange -n production
```

---

## 실전 리소스 관리 체크리스트

### 네임스페이스 설정 순서

1. `LimitRange` 설정 (컨테이너 기본값 및 최대값)
2. `ResourceQuota` 설정 (네임스페이스 총량)
3. 각 Deployment의 `resources` 설정 확인

### Guaranteed QoS를 위한 설정

```yaml
resources:
  requests:
    cpu: "200m"
    memory: "256Mi"
  limits:
    cpu: "200m"      # requests와 동일
    memory: "256Mi"  # requests와 동일
```

### 모니터링 확인 명령어

```bash
# 노드별 리소스 사용량
kubectl top nodes

# Pod별 리소스 사용량
kubectl top pods -n production --sort-by=memory

# 컨테이너별 리소스 사용량
kubectl top pods -n production --containers

# 리소스 할당 현황
kubectl describe nodes | grep -A 5 "Allocated resources"

# HPA 상태
kubectl get hpa -n production

# VPA 권장값
kubectl describe vpa -n production
```

---

## KEDA (Kubernetes Event-Driven Autoscaling) 소개

HPA보다 다양한 이벤트 소스 기반 스케일링을 지원합니다.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: my-app-scaler
  namespace: production
spec:
  scaleTargetRef:
    name: my-app
  minReplicaCount: 0    # 0으로 스케일 다운 가능
  maxReplicaCount: 50
  triggers:
    # SQS 기반
    - type: aws-sqs-queue
      metadata:
        queueURL: https://sqs.ap-northeast-2.amazonaws.com/123456789/my-queue
        queueLength: "10"
        awsRegion: ap-northeast-2
    # Kafka 기반
    - type: kafka
      metadata:
        bootstrapServers: kafka:9092
        consumerGroup: my-app-group
        topic: my-topic
        lagThreshold: "100"
```

KEDA는 이벤트가 없을 때 0으로 스케일 다운할 수 있어 비용 절감에 효과적입니다.
