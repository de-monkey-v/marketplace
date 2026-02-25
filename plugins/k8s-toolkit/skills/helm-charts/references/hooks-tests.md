# Helm Hooks와 테스트

Helm Hooks는 릴리스 라이프사이클의 특정 시점에 Kubernetes 리소스를 실행합니다. `helm test`는 배포된 차트를 검증합니다.

## Hook 유형

| Hook 이름 | 실행 시점 |
|-----------|----------|
| `pre-install` | 템플릿 렌더링 후, 리소스 생성 전 |
| `post-install` | 모든 리소스 생성 후 |
| `pre-upgrade` | 업그레이드 전, 리소스 업데이트 전 |
| `post-upgrade` | 업그레이드 완료 후 |
| `pre-delete` | 삭제 요청 후, 리소스 삭제 전 |
| `post-delete` | 모든 리소스 삭제 후 |
| `pre-rollback` | 롤백 전 |
| `post-rollback` | 롤백 완료 후 |
| `test` | `helm test` 명령 실행 시 |

## Hook Annotations

Hook은 Kubernetes 리소스의 annotation으로 정의됩니다:

```yaml
annotations:
  # Hook 유형 (복수 지정 가능)
  "helm.sh/hook": pre-install,pre-upgrade

  # Hook 실행 순서 (낮은 숫자 먼저, 음수 가능)
  "helm.sh/hook-weight": "-5"

  # Hook 완료 후 삭제 정책
  "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
```

### hook-delete-policy 옵션

| 정책 | 설명 |
|------|------|
| `before-hook-creation` | 새 Hook 실행 전 이전 Hook 리소스 삭제 (기본 권장) |
| `hook-succeeded` | Hook 성공 시 삭제 |
| `hook-failed` | Hook 실패 시 삭제 |

## 일반적인 Hook 패턴

### DB 마이그레이션 (pre-upgrade, pre-install)

```yaml
# templates/job-migration.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-app.fullname" . }}-migration
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": pre-install,pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  ttlSecondsAfterFinished: 300  # 5분 후 자동 삭제
  backoffLimit: 3
  template:
    metadata:
      name: {{ include "my-app.fullname" . }}-migration
      labels:
        {{- include "my-app.selectorLabels" . | nindent 8 }}
    spec:
      restartPolicy: Never
      serviceAccountName: {{ include "my-app.serviceAccountName" . }}
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      containers:
        - name: migration
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          command: ["python", "manage.py", "migrate", "--noinput"]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ include "my-app.fullname" . }}-db-secret
                  key: url
          resources:
            limits:
              cpu: 500m
              memory: 512Mi
            requests:
              cpu: 100m
              memory: 128Mi
```

### 초기 데이터 로드 (post-install)

```yaml
# templates/job-seed.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-app.fullname" . }}-seed
  annotations:
    "helm.sh/hook": post-install
    "helm.sh/hook-weight": "5"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  ttlSecondsAfterFinished: 600
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: seed
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          command: ["python", "manage.py", "loaddata", "initial_data"]
          envFrom:
            - secretRef:
                name: {{ include "my-app.fullname" . }}
```

### 정리 작업 (pre-delete)

```yaml
# templates/job-cleanup.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-app.fullname" . }}-cleanup
  annotations:
    "helm.sh/hook": pre-delete
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: cleanup
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          command: ["python", "manage.py", "cleanup"]
```

### Hook에서 Secret 생성 (pre-install)

```yaml
# templates/secret-generator.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-app.fullname" . }}-secret-gen
  annotations:
    "helm.sh/hook": pre-install
    "helm.sh/hook-weight": "-10"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      serviceAccountName: {{ include "my-app.fullname" . }}-secret-gen
      containers:
        - name: secret-gen
          image: bitnami/kubectl:latest
          command:
            - /bin/sh
            - -c
            - |
              kubectl create secret generic {{ include "my-app.fullname" . }}-generated \
                --from-literal=jwt-secret=$(openssl rand -base64 32) \
                --from-literal=api-key=$(openssl rand -hex 32) \
                --namespace {{ .Release.Namespace }} \
                --dry-run=client -o yaml | kubectl apply -f -
```

## helm test 작성

`helm test`는 `test` Hook이 달린 Pod를 실행하여 배포를 검증합니다.

### 기본 연결 테스트

```yaml
# templates/tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-app.fullname" . }}-test-connection"
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  restartPolicy: Never
  containers:
    - name: test-connection
      image: busybox:1.35
      command:
        - /bin/sh
        - -c
        - |
          # HTTP 연결 테스트
          wget --timeout=5 --tries=3 \
            http://{{ include "my-app.fullname" . }}:{{ .Values.service.port }}/health \
            -O /dev/null
          echo "Connection test passed!"
```

### API 엔드포인트 테스트

```yaml
# templates/tests/test-api.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-app.fullname" . }}-test-api"
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  restartPolicy: Never
  containers:
    - name: test-api
      image: curlimages/curl:8.1.0
      command:
        - /bin/sh
        - -c
        - |
          BASE_URL="http://{{ include "my-app.fullname" . }}:{{ .Values.service.port }}"

          # 헬스체크 엔드포인트
          echo "Testing health endpoint..."
          curl -f "$BASE_URL/health" || exit 1

          # API 버전 확인
          echo "Testing API version..."
          response=$(curl -s "$BASE_URL/api/version")
          echo "$response" | grep -q "version" || exit 1

          echo "All API tests passed!"
```

### DB 연결 테스트 (PostgreSQL)

```yaml
# templates/tests/test-database.yaml
{{- if .Values.postgresql.enabled }}
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-app.fullname" . }}-test-db"
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  restartPolicy: Never
  containers:
    - name: test-db
      image: postgres:15
      command:
        - /bin/sh
        - -c
        - |
          PGPASSWORD=$DB_PASSWORD psql \
            -h {{ include "my-app.fullname" . }}-postgresql \
            -U {{ .Values.postgresql.auth.username }} \
            -d {{ .Values.postgresql.auth.database }} \
            -c "SELECT 1" || exit 1
          echo "Database connection test passed!"
      env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: {{ include "my-app.fullname" . }}-postgresql
              key: password
{{- end }}
```

## helm test 실행

```bash
# 테스트 실행
helm test my-release

# 로그 포함
helm test my-release --logs

# 타임아웃 설정
helm test my-release --timeout 5m

# 특정 네임스페이스
helm test my-release --namespace my-namespace
```

## 릴리스 라이프사이클 전체 흐름

```
helm install
  ├── 1. Chart 렌더링
  ├── 2. CRD 설치 (crds/)
  ├── 3. pre-install hooks 실행 (weight 순서)
  ├── 4. Kubernetes 리소스 생성
  ├── 5. post-install hooks 실행
  └── 6. NOTES.txt 출력

helm upgrade
  ├── 1. Chart 렌더링
  ├── 2. pre-upgrade hooks 실행
  ├── 3. Kubernetes 리소스 업데이트
  ├── 4. post-upgrade hooks 실행
  └── 5. NOTES.txt 출력

helm rollback
  ├── 1. pre-rollback hooks 실행
  ├── 2. 이전 버전으로 복원
  └── 3. post-rollback hooks 실행

helm uninstall
  ├── 1. pre-delete hooks 실행
  ├── 2. 리소스 삭제
  └── 3. post-delete hooks 실행

helm test
  └── test hooks 실행 (test annotation Pod 실행)
```

## Hook 실행 대기 (--wait)

기본적으로 Helm은 Hook 완료를 기다립니다. Job이 완료되거나 실패할 때까지 대기합니다:

```bash
# Hook 완료 대기 (기본 5분)
helm upgrade --install my-release ./my-app --wait --timeout 10m

# Hook 실패 시 자동 롤백
helm upgrade --install my-release ./my-app --atomic --timeout 10m
```
