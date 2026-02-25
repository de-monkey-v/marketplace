# Workloads 상세 패턴

Deployment, StatefulSet, DaemonSet, Job, CronJob의 상세 패턴과 실전 YAML 예제를 제공합니다.

---

## Deployment

### 기본 구조

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: production
  labels:
    app.kubernetes.io/name: my-app
    app.kubernetes.io/version: "1.2.0"
    app.kubernetes.io/component: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: my-app
  template:
    metadata:
      labels:
        app.kubernetes.io/name: my-app
        app.kubernetes.io/version: "1.2.0"
    spec:
      serviceAccountName: my-app
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: my-app
          image: my-app:1.2.0
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          livenessProbe:
            httpGet:
              path: /healthz
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
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
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

### 업데이트 전략

**RollingUpdate (기본값, 권장):**
```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # 최대 초과 Pod 수 (또는 %)
      maxUnavailable: 0    # 최대 불가용 Pod 수 (0이면 무중단 배포)
```

- `maxUnavailable: 0` + `maxSurge: 1` 조합 = 무중단 배포
- 트래픽이 많은 프로덕션에서는 `maxUnavailable: 0` 권장
- `maxSurge`를 높이면 배포 속도가 빨라지나 리소스 사용량이 증가

**Recreate (다운타임 허용 시):**
```yaml
spec:
  strategy:
    type: Recreate
```

- 모든 기존 Pod를 종료 후 새 Pod 생성
- 단일 인스턴스 앱이나 DB 스키마 변경이 필요한 경우에 사용
- 다운타임 발생함

### 프로브 상세 설정

**httpGet 프로브:**
```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
    httpHeaders:
      - name: Custom-Header
        value: check
  initialDelaySeconds: 15
  periodSeconds: 20
  timeoutSeconds: 5
  successThreshold: 1
  failureThreshold: 3
```

**tcpSocket 프로브 (비HTTP 서비스용):**
```yaml
livenessProbe:
  tcpSocket:
    port: 5432
  initialDelaySeconds: 30
  periodSeconds: 10
```

**exec 프로브 (커맨드 실행):**
```yaml
livenessProbe:
  exec:
    command:
      - /bin/sh
      - -c
      - redis-cli ping
  initialDelaySeconds: 5
  periodSeconds: 5
```

**startupProbe (느린 시작 앱):**
```yaml
startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30   # 30 * 10s = 300초 대기
  periodSeconds: 10
```

---

## StatefulSet

상태를 가진 애플리케이션(데이터베이스, 메시지 큐 등)에 사용합니다.

### 기본 구조

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
  namespace: production
spec:
  serviceName: postgresql-headless  # Headless Service 이름 (필수)
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: postgresql
  podManagementPolicy: OrderedReady  # 또는 Parallel
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 0  # Canary 배포 시 활용
  template:
    metadata:
      labels:
        app.kubernetes.io/name: postgresql
    spec:
      containers:
        - name: postgresql
          image: postgres:15
          ports:
            - name: postgresql
              containerPort: 5432
          env:
            - name: POSTGRES_DB
              value: mydb
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: postgresql-secret
                  key: username
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgresql-secret
                  key: password
          resources:
            requests:
              cpu: "250m"
              memory: "512Mi"
            limits:
              cpu: "1"
              memory: "2Gi"
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
          livenessProbe:
            exec:
              command:
                - /bin/sh
                - -c
                - pg_isready -U postgres
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            exec:
              command:
                - /bin/sh
                - -c
                - pg_isready -U postgres
            initialDelaySeconds: 5
            periodSeconds: 5
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast-ssd
        resources:
          requests:
            storage: 50Gi
```

### 안정적 네트워크 ID

StatefulSet은 Pod에 순서 기반 이름을 부여합니다:
- `postgresql-0`, `postgresql-1`, `postgresql-2`

Headless Service를 통해 DNS로 직접 접근 가능합니다:
- `postgresql-0.postgresql-headless.production.svc.cluster.local`

**Headless Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgresql-headless
  namespace: production
spec:
  clusterIP: None   # Headless
  selector:
    app.kubernetes.io/name: postgresql
  ports:
    - port: 5432
      targetPort: 5432
```

### podManagementPolicy

- `OrderedReady` (기본값): Pod를 순서대로 생성/삭제. 이전 Pod가 Ready 상태여야 다음 생성.
- `Parallel`: 모든 Pod를 동시에 생성/삭제. 초기화 순서가 중요하지 않은 경우.

---

## DaemonSet

모든 (또는 특정) 노드에 하나씩 Pod를 실행합니다. 로그 수집기, 모니터링 에이전트에 사용합니다.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: node-exporter
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
  template:
    metadata:
      labels:
        app.kubernetes.io/name: node-exporter
    spec:
      hostNetwork: true
      hostPID: true
      tolerations:
        - key: node-role.kubernetes.io/control-plane
          operator: Exists
          effect: NoSchedule
        - key: node-role.kubernetes.io/master
          operator: Exists
          effect: NoSchedule
      containers:
        - name: node-exporter
          image: prom/node-exporter:v1.7.0
          args:
            - --path.procfs=/host/proc
            - --path.sysfs=/host/sys
          ports:
            - name: metrics
              containerPort: 9100
          resources:
            requests:
              cpu: "50m"
              memory: "64Mi"
            limits:
              cpu: "200m"
              memory: "256Mi"
          securityContext:
            readOnlyRootFilesystem: true
          volumeMounts:
            - name: proc
              mountPath: /host/proc
              readOnly: true
            - name: sys
              mountPath: /host/sys
              readOnly: true
      volumes:
        - name: proc
          hostPath:
            path: /proc
        - name: sys
          hostPath:
            path: /sys
```

### 특정 노드만 선택

**nodeSelector로 선택:**
```yaml
spec:
  template:
    spec:
      nodeSelector:
        kubernetes.io/os: linux
        node-type: worker
```

**nodeAffinity로 선택:**
```yaml
spec:
  template:
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
              - matchExpressions:
                  - key: node-type
                    operator: In
                    values: ["gpu", "high-memory"]
```

---

## Job

일회성 배치 작업에 사용합니다.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
  namespace: production
spec:
  backoffLimit: 3          # 실패 시 재시도 횟수
  completions: 1           # 성공 완료 횟수
  parallelism: 1           # 동시 실행 Pod 수
  activeDeadlineSeconds: 600  # 최대 실행 시간 (초)
  ttlSecondsAfterFinished: 3600  # 완료 후 자동 삭제 시간
  template:
    spec:
      restartPolicy: OnFailure  # Never 또는 OnFailure
      containers:
        - name: migration
          image: my-app:1.2.0
          command: ["python", "manage.py", "migrate"]
          resources:
            requests:
              cpu: "100m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          envFrom:
            - configMapRef:
                name: my-app-config
            - secretRef:
                name: my-app-secret
```

### 병렬 Job

```yaml
spec:
  completions: 10    # 총 10번 성공
  parallelism: 3     # 동시에 3개 실행
  backoffLimit: 6
```

---

## CronJob

주기적으로 Job을 실행합니다.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job
  namespace: production
spec:
  schedule: "0 2 * * *"          # 매일 새벽 2시
  timeZone: "Asia/Seoul"         # 타임존 (k8s 1.27+)
  concurrencyPolicy: Forbid      # Allow / Forbid / Replace
  successfulJobsHistoryLimit: 3  # 성공 Job 보관 수
  failedJobsHistoryLimit: 1      # 실패 Job 보관 수
  startingDeadlineSeconds: 120   # 스케줄 지연 허용 시간 (초)
  jobTemplate:
    spec:
      backoffLimit: 2
      activeDeadlineSeconds: 3600
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: backup
              image: backup-tool:latest
              command: ["/scripts/backup.sh"]
              resources:
                requests:
                  cpu: "200m"
                  memory: "256Mi"
                limits:
                  cpu: "500m"
                  memory: "512Mi"
```

### schedule 문법

```
┌───────────── 분 (0 - 59)
│ ┌───────────── 시 (0 - 23)
│ │ ┌───────────── 일 (1 - 31)
│ │ │ ┌───────────── 월 (1 - 12)
│ │ │ │ ┌───────────── 요일 (0 - 6, 0=일요일)
│ │ │ │ │
* * * * *
```

| 표현 | 의미 |
|------|------|
| `0 * * * *` | 매 시간 정각 |
| `*/15 * * * *` | 15분마다 |
| `0 9 * * 1-5` | 평일 오전 9시 |
| `0 0 1 * *` | 매월 1일 자정 |
| `@daily` | 매일 자정 (`0 0 * * *`) |
| `@hourly` | 매 시간 (`0 * * * *`) |

### concurrencyPolicy

- `Allow`: 이전 Job이 실행 중이어도 새 Job 생성
- `Forbid`: 이전 Job이 실행 중이면 새 Job 건너뜀
- `Replace`: 이전 Job을 종료하고 새 Job 생성

---

## 공통: 토폴로지 분산 제약

Pod를 여러 가용 영역에 고르게 분산합니다.

```yaml
spec:
  template:
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: my-app
        - maxSkew: 1
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: my-app
```

- `maxSkew`: 가장 많은 Pod와 가장 적은 Pod 수의 차이 허용값
- `whenUnsatisfiable: DoNotSchedule`: 제약을 만족할 수 없으면 스케줄링 거부
- `whenUnsatisfiable: ScheduleAnyway`: 제약을 만족할 수 없어도 최선의 노드에 스케줄링

## 공통: 그레이스풀 종료

```yaml
spec:
  template:
    spec:
      terminationGracePeriodSeconds: 30
      containers:
        - name: app
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 5"]
```

`preStop` hook으로 Kubernetes가 엔드포인트를 제거할 시간을 줍니다.
