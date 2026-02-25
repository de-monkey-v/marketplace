# 의존성 관리 가이드

Helm 차트 의존성은 다른 차트를 서브차트로 포함하여 복잡한 애플리케이션 스택을 관리합니다.

## Chart.yaml dependencies 필드

```yaml
dependencies:
  # 기본 의존성 (Helm 레포지토리)
  - name: postgresql
    version: "12.5.6"           # SemVer 범위 지정 가능 ("^12.0.0", "12.x.x")
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled  # values.yaml의 bool 값으로 활성화 제어
    alias: db                   # 별칭 (여러 동일 차트 사용 시)

  # OCI 레지스트리 의존성
  - name: redis
    version: "17.11.3"
    repository: "oci://registry-1.docker.io/bitnamicharts"
    condition: redis.enabled

  # 로컬 차트 의존성
  - name: common-lib
    version: "0.1.0"
    repository: "file://../common-lib"

  # 태그로 그룹 활성화
  - name: monitoring
    version: "^1.0.0"
    repository: "https://charts.example.com"
    tags:
      - monitoring
      - observability

  # 여러 인스턴스 (alias 활용)
  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    alias: primary-db
    condition: primaryDb.enabled

  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    alias: replica-db
    condition: replicaDb.enabled
```

## 의존성 관리 명령어

```bash
# 레포지토리 추가
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# 의존성 다운로드 (Chart.lock 생성/갱신)
helm dependency update ./my-app
# 결과: charts/ 디렉토리에 .tgz 파일 다운로드

# Chart.lock 기반으로 빌드 (버전 고정)
helm dependency build ./my-app

# 의존성 목록 확인
helm dependency list ./my-app
```

**Chart.lock 파일 역할:**

```yaml
# Chart.lock (자동 생성, VCS에 커밋 권장)
dependencies:
  - name: postgresql
    repository: https://charts.bitnami.com/bitnami
    version: 12.5.6
digest: sha256:abc123...  # 무결성 검증
generated: "2024-01-15T10:00:00.000000000Z"
```

## condition과 tags로 선택적 활성화

### condition 사용

```yaml
# Chart.yaml
dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled  # values.yaml의 키 경로

  - name: redis
    version: "17.x.x"
    repository: "oci://registry-1.docker.io/bitnamicharts"
    condition: redis.enabled
```

```yaml
# values.yaml
postgresql:
  enabled: true    # postgresql 서브차트 활성화
  auth:
    username: myuser
    database: mydb
    existingSecret: my-postgresql-secret

redis:
  enabled: false   # redis 서브차트 비활성화
```

### tags 사용 (그룹 제어)

```yaml
# Chart.yaml
dependencies:
  - name: prometheus
    version: "^25.0.0"
    repository: "https://prometheus-community.github.io/helm-charts"
    tags:
      - monitoring

  - name: grafana
    version: "^7.0.0"
    repository: "https://grafana.github.io/helm-charts"
    tags:
      - monitoring
```

```yaml
# values.yaml
tags:
  monitoring: false  # 그룹 전체 비활성화

# 또는 배포 시 활성화
# helm install ... --set tags.monitoring=true
```

## Subchart 통신 패턴

### 부모에서 서브차트로 값 전달

서브차트 이름(또는 alias)을 키로 사용하여 값을 전달합니다:

```yaml
# values.yaml (부모 차트)
postgresql:
  enabled: true
  auth:
    username: myapp
    database: myapp_db
    existingSecret: ""
    # 평문 비밀번호는 프로덕션에서 사용하지 않음
    # password: "changeme"
  primary:
    persistence:
      enabled: true
      size: 10Gi
  resources:
    requests:
      memory: 256Mi
      cpu: 250m
    limits:
      memory: 512Mi
      cpu: 500m
```

### global 값 공유

`global` 키는 모든 서브차트에 자동으로 전파됩니다:

```yaml
# 부모 values.yaml
global:
  imageRegistry: "my-registry.example.com"
  imagePullSecrets:
    - name: registry-secret
  storageClass: "fast-ssd"

# 서브차트에서 global 접근
# image: "{{ .Values.global.imageRegistry }}/my-image:latest"
```

### import-values (서브차트 → 부모)

서브차트의 값을 부모 차트로 내보냅니다:

```yaml
# Chart.yaml
dependencies:
  - name: my-subchart
    version: "1.0.0"
    repository: "https://charts.example.com"
    import-values:
      # 서브차트의 exports.data를 부모의 mydata로
      - child: exports.data
        parent: mydata

      # 단순 내보내기
      - defaults
```

```yaml
# 서브차트 values.yaml
exports:
  data:
    host: "subchart-service"
    port: 8080
```

## 로컬 차트 의존성

개발 중 로컬 차트를 의존성으로 사용합니다:

```
parent-chart/
├── Chart.yaml
├── values.yaml
└── charts/              # 또는 file:// 참조

../common-lib/           # 형제 디렉토리
├── Chart.yaml
└── templates/
```

```yaml
# Chart.yaml
dependencies:
  - name: common-lib
    version: "0.1.0"
    repository: "file://../common-lib"
```

```bash
# 로컬 의존성 빌드
helm dependency build ./parent-chart
# charts/common-lib-0.1.0.tgz 생성
```

## OCI 레지스트리 사용

Helm 3.8+부터 OCI 레지스트리를 기본 지원합니다:

```bash
# OCI 레지스트리 로그인
helm registry login registry.example.com \
  --username myuser \
  --password mypassword

# OCI 차트 설치
helm install my-release \
  oci://registry.example.com/charts/my-app \
  --version 1.0.0

# OCI 차트 풀
helm pull oci://registry.example.com/charts/my-app --version 1.0.0

# OCI 차트 푸시
helm push my-app-1.0.0.tgz oci://registry.example.com/charts
```

```yaml
# Chart.yaml에서 OCI 의존성
dependencies:
  - name: redis
    version: "17.11.3"
    repository: "oci://registry-1.docker.io/bitnamicharts"
```

## 의존성이 있는 차트 배포

```bash
# 의존성 다운로드 후 설치
helm dependency update ./my-app
helm install my-release ./my-app \
  --set postgresql.enabled=true \
  --set redis.enabled=false

# 의존성 비활성화 옵션
helm install my-release ./my-app \
  --set postgresql.enabled=false \
  --set-string postgresql.external.host=external-db.example.com \
  --set-string postgresql.external.port=5432
```

## 외부 서비스 전환 패턴

내장 서브차트와 외부 서비스를 전환 가능하게 설계합니다:

```yaml
# values.yaml
postgresql:
  enabled: true  # false로 설정하면 외부 DB 사용

# 외부 DB 설정 (postgresql.enabled=false 시)
externalDatabase:
  host: ""
  port: 5432
  user: myapp
  database: myapp_db
  existingSecret: my-db-secret
  existingSecretKey: password
```

```yaml
# templates/deployment.yaml
env:
  - name: DB_HOST
    value: >-
      {{- if .Values.postgresql.enabled }}
      {{- include "my-app.fullname" . }}-postgresql
      {{- else }}
      {{- .Values.externalDatabase.host }}
      {{- end }}
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: >-
          {{- if .Values.postgresql.enabled }}
          {{- include "my-app.fullname" . }}-postgresql
          {{- else }}
          {{- .Values.externalDatabase.existingSecret }}
          {{- end }}
        key: >-
          {{- if .Values.postgresql.enabled -}}
          postgres-password
          {{- else -}}
          {{ .Values.externalDatabase.existingSecretKey }}
          {{- end }}
```
