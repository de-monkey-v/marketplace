---
name: helm-charts
description: "This skill should be used when the user asks to \"helm chart 만들어\", \"차트 구조\", \"values.yaml 설계\", \"helm template\", \"helm 개발\", \"chart 작성\", \"helm install\", \"helm upgrade\", or mentions Helm chart development and management. Provides guidance for Helm chart authoring and best practices."
version: 0.1.0
---

# Helm Chart 개발 가이드

Helm은 Kubernetes 패키지 매니저로, 복잡한 애플리케이션 배포를 재사용 가능한 차트로 패키징합니다. 이 가이드는 프로덕션 수준의 Helm 차트를 작성하고 관리하는 핵심 절차를 다룹니다.

## Chart 개발 핵심 원칙

**버전 관리 (SemVer)**

`Chart.yaml`의 `version` 필드는 차트 자체의 버전을, `appVersion`은 패키징되는 애플리케이션 버전을 나타냅니다. 두 버전 모두 SemVer 2.0.0을 따릅니다.

- 하위 호환 버그 수정 → patch 증가 (1.0.0 → 1.0.1)
- 하위 호환 기능 추가 → minor 증가 (1.0.0 → 1.1.0)
- 하위 비호환 변경 → major 증가 (1.0.0 → 2.0.0)

**네이밍 컨벤션**

- 차트 이름: kebab-case 소문자 (`my-app`, `nginx-ingress`)
- 리소스 이름: `{{ include "chart.fullname" . }}` 헬퍼 사용
- 레이블: Kubernetes 권고 레이블 포함 (`app.kubernetes.io/name`, `app.kubernetes.io/instance`)

## Chart.yaml 필수 필드

```yaml
apiVersion: v2          # Helm 3 필수
name: my-app            # kebab-case
version: 0.1.0          # 차트 버전 (SemVer)
appVersion: "1.0.0"     # 앱 버전 (문자열 권장)
description: A Helm chart for my-app
type: application       # application | library
```

선택적이지만 권장 필드:

```yaml
maintainers:
  - name: Team Name
    email: team@example.com
keywords:
  - webapp
  - backend
home: https://github.com/org/my-app
sources:
  - https://github.com/org/my-app
```

상세 내용은 [`references/chart-structure.md`](references/chart-structure.md)를 참조합니다.

## 표준 디렉토리 구조

```
my-app/
├── Chart.yaml           # 차트 메타데이터 (필수)
├── values.yaml          # 기본 설정값 (필수)
├── charts/              # 의존 차트 디렉토리
├── crds/                # CRD 정의 (설치 순서 보장)
├── templates/           # Kubernetes 매니페스트 템플릿
│   ├── NOTES.txt        # 설치 후 안내 메시지 (필수)
│   ├── _helpers.tpl     # 재사용 템플릿 헬퍼 (필수)
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── serviceaccount.yaml
│   ├── hpa.yaml
│   └── tests/
│       └── test-connection.yaml
└── .helmignore          # 패키징 제외 파일
```

## values.yaml 설계 기본 원칙

계층 구조를 사용해 설정을 논리적으로 그룹화합니다:

```yaml
# 이미지 설정
image:
  repository: nginx
  tag: "1.21"
  pullPolicy: IfNotPresent

# 복제본 수
replicaCount: 1

# 서비스 설정
service:
  type: ClusterIP
  port: 80

# 인그레스 설정
ingress:
  enabled: false
  className: ""
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: Prefix

# 리소스 제한
resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 128Mi

# 보안 컨텍스트 (보안 기본값 설정)
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
```

values.yaml 설계 패턴 상세 내용은 [`references/values-design.md`](references/values-design.md)를 참조합니다.

## 핵심 템플릿 패턴

**`_helpers.tpl` 기본 구조:**

```yaml
{{/*
Chart의 전체 이름을 반환합니다.
*/}}
{{- define "my-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
공통 레이블
*/}}
{{- define "my-app.labels" -}}
helm.sh/chart: {{ include "my-app.chart" . }}
{{ include "my-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
셀렉터 레이블
*/}}
{{- define "my-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "my-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

Go 템플릿 패턴 상세 내용은 [`references/template-patterns.md`](references/template-patterns.md)를 참조합니다.

## 보안 고려사항

**RBAC 포함 (조건부 생성):**

```yaml
# values.yaml
serviceAccount:
  create: true
  annotations: {}
  name: ""
```

```yaml
# templates/serviceaccount.yaml
{{- if .Values.serviceAccount.create -}}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "my-app.serviceAccountName" . }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
  {{- with .Values.serviceAccount.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
{{- end }}
```

**Secrets 처리 원칙:**

- 비밀값을 values.yaml에 평문으로 저장하지 않습니다
- `helm-secrets` 또는 외부 시크릿 매니저(External Secrets Operator)를 사용합니다
- 환경 변수보다 파일 마운트를 선호합니다

```yaml
# 권장: 기존 Secret 참조
envFrom:
  - secretRef:
      name: {{ .Values.existingSecret | default (include "my-app.fullname" .) }}
```

## 빠른 시작 명령어

**새 차트 생성:**

```bash
helm create my-app
```

**차트 검증:**

```bash
# 린트 검사
helm lint ./my-app

# 템플릿 렌더링 확인
helm template my-release ./my-app --values values-dev.yaml

# 드라이런 배포
helm install my-release ./my-app --dry-run --debug
```

**배포 및 업그레이드:**

```bash
# 초기 설치
helm install my-release ./my-app \
  --namespace my-namespace \
  --create-namespace \
  --values values-prod.yaml

# 업그레이드 (없으면 설치)
helm upgrade --install my-release ./my-app \
  --namespace my-namespace \
  --values values-prod.yaml \
  --atomic \
  --wait \
  --timeout 5m
```

**의존성 관리:**

```bash
# 의존 차트 다운로드
helm dependency update ./my-app

# 의존 차트 빌드 (로컬)
helm dependency build ./my-app
```

의존성 관리 상세 내용은 [`references/dependencies.md`](references/dependencies.md)를 참조합니다.

## Helm Hooks와 테스트

**DB 마이그레이션 Hook 예시:**

```yaml
# templates/job-migration.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-app.fullname" . }}-migration
  annotations:
    "helm.sh/hook": pre-upgrade,pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
```

**helm test 작성:**

```yaml
# templates/tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-app.fullname" . }}-test-connection"
  annotations:
    "helm.sh/hook": test
spec:
  restartPolicy: Never
  containers:
    - name: wget
      image: busybox
      command: ['wget']
      args: ['{{ include "my-app.fullname" . }}:{{ .Values.service.port }}']
```

Hooks와 테스트 상세 내용은 [`references/hooks-tests.md`](references/hooks-tests.md)를 참조합니다.

## 프로덕션 배포 체크리스트

배포 전 다음 항목을 확인합니다:

- `helm lint` 통과
- `helm template` 렌더링 오류 없음
- `kubeval` 또는 `kubeconform`으로 스키마 검증
- `values.schema.json` 입력값 검증 정의
- 리소스 requests/limits 설정
- `podSecurityContext` 및 `securityContext` 설정
- `livenessProbe` / `readinessProbe` 설정
- `NetworkPolicy` 고려

프로덕션 모범 사례 전체 내용은 [`references/best-practices.md`](references/best-practices.md)를 참조합니다.

## 참고 자료

### Reference Files

- **[`references/chart-structure.md`](references/chart-structure.md)** - Chart.yaml 전체 필드, 디렉토리 구조, 라이브러리 차트 패턴
- **[`references/values-design.md`](references/values-design.md)** - values.yaml 설계 패턴, 환경별 분리, JSON Schema 검증
- **[`references/template-patterns.md`](references/template-patterns.md)** - Go 템플릿 문법, 내장 함수, 조건부 렌더링, 반복문
- **[`references/dependencies.md`](references/dependencies.md)** - 차트 의존성 관리, subchart 통신, OCI 레지스트리
- **[`references/hooks-tests.md`](references/hooks-tests.md)** - Hook 유형, Hook annotations, helm test 작성법
- **[`references/best-practices.md`](references/best-practices.md)** - 프로덕션 릴리스 전략, 보안 하드닝, CI/CD 통합, GitOps
