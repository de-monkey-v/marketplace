# Chart 구조 상세 가이드

Helm 차트의 디렉토리 구조와 핵심 파일들을 상세하게 설명합니다.

## Chart.yaml 전체 필드

`Chart.yaml`은 차트 메타데이터를 정의하는 필수 파일입니다.

```yaml
# Helm 3에서는 v2 필수
apiVersion: v2

# 차트 이름 (kebab-case, 소문자)
name: my-app

# 차트 버전 (SemVer 2.0.0)
version: 1.2.3

# 패키징된 애플리케이션 버전 (문자열로 명시 권장)
appVersion: "2.5.1"

# 차트 설명 (한 줄 요약)
description: A Helm chart for deploying my-app on Kubernetes

# 차트 유형: application (기본) 또는 library
type: application

# 키워드 (검색 및 분류)
keywords:
  - webapp
  - backend
  - nodejs

# 홈페이지
home: https://github.com/myorg/my-app

# 소스 코드 링크 (복수 가능)
sources:
  - https://github.com/myorg/my-app

# 관리자 정보
maintainers:
  - name: Platform Team
    email: platform@example.com
    url: https://example.com/platform

# 아이콘 URL (SVG 또는 PNG)
icon: https://example.com/icon.png

# 의존 차트 목록
dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
    alias: db

  - name: redis
    version: "17.x.x"
    repository: "oci://registry-1.docker.io/bitnamicharts"
    condition: redis.enabled

# 차트 어노테이션 (Artifact Hub 등)
annotations:
  artifacthub.io/changes: |
    - kind: added
      description: Support for HPA
  artifacthub.io/containsSecurityUpdates: "true"
  artifacthub.io/license: Apache-2.0
```

### apiVersion 차이점

| apiVersion | Helm 버전 | 차이점 |
|-----------|----------|--------|
| v1 | Helm 2/3 | 기본 필드만 지원 |
| v2 | Helm 3 전용 | `type`, `dependencies`, `condition` 지원 |

항상 `apiVersion: v2`를 사용합니다. Helm 3만 지원하며 모든 기능을 활용할 수 있습니다.

## 표준 디렉토리 구조

```
my-app/
├── Chart.yaml                    # 차트 메타데이터 (필수)
├── Chart.lock                    # 의존성 잠금 파일 (helm dep update 생성)
├── values.yaml                   # 기본 설정값 (필수)
├── values.schema.json            # values.yaml JSON Schema 검증
├── .helmignore                   # 패키징 제외 파일 목록
├── charts/                       # 의존 차트 (Chart.lock 기반 다운로드)
│   ├── postgresql-12.1.0.tgz
│   └── redis-17.0.0.tgz
├── crds/                         # CRD 정의 (템플릿보다 먼저 설치됨)
│   └── my-custom-resource.yaml
└── templates/                    # Kubernetes 매니페스트 템플릿
    ├── NOTES.txt                 # 설치 후 사용자 안내 메시지 (필수)
    ├── _helpers.tpl              # 재사용 템플릿 정의 (필수)
    ├── deployment.yaml
    ├── service.yaml
    ├── serviceaccount.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    ├── secret.yaml
    ├── hpa.yaml
    ├── pdb.yaml
    └── tests/
        └── test-connection.yaml  # helm test 용 Pod
```

### 파일명 컨벤션

- 일반 매니페스트: `lowercase.yaml` (예: `deployment.yaml`, `service.yaml`)
- 헬퍼 파일: `_` 접두사 (예: `_helpers.tpl`) — 렌더링에서 제외됨
- 테스트: `tests/` 서브디렉토리에 배치

## 필수 파일 상세

### templates/NOTES.txt

설치/업그레이드 완료 후 사용자에게 표시되는 안내 메시지입니다. 템플릿 문법을 사용할 수 있습니다.

```
Thank you for installing {{ .Chart.Name }}.

Your release is named {{ .Release.Name }}.

To get the application URL, run:
{{- if .Values.ingress.enabled }}
{{- range $host := .Values.ingress.hosts }}
  http{{ if $.Values.ingress.tls }}s{{ end }}://{{ $host.host }}
{{- end }}
{{- else if contains "NodePort" .Values.service.type }}
  export NODE_PORT=$(kubectl get --namespace {{ .Release.Namespace }} -o jsonpath="{.spec.ports[0].nodePort}" services {{ include "my-app.fullname" . }})
  export NODE_IP=$(kubectl get nodes --namespace {{ .Release.Namespace }} -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT
{{- else if contains "LoadBalancer" .Values.service.type }}
  NOTE: It may take a few minutes for the LoadBalancer IP to be available.
  kubectl get --namespace {{ .Release.Namespace }} svc -w {{ include "my-app.fullname" . }}
{{- else if contains "ClusterIP" .Values.service.type }}
  kubectl --namespace {{ .Release.Namespace }} port-forward svc/{{ include "my-app.fullname" . }} 8080:{{ .Values.service.port }}
  Visit http://127.0.0.1:8080
{{- end }}
```

### templates/_helpers.tpl

재사용 가능한 named template을 정의합니다. `_` 접두사로 렌더링에서 제외됩니다.

```yaml
{{/*
앱 이름 (63자 제한)
*/}}
{{- define "my-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
릴리스명을 포함한 전체 이름
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
차트 레이블 (이름 + 버전)
*/}}
{{- define "my-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
공통 레이블 (권고 레이블 포함)
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
Selector 레이블 (Deployment selector에 사용)
*/}}
{{- define "my-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "my-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
ServiceAccount 이름
*/}}
{{- define "my-app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "my-app.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
```

## 라이브러리 차트 패턴

라이브러리 차트는 공통 템플릿을 재사용하기 위한 차트입니다. 직접 배포되지 않고 다른 차트의 의존성으로만 사용됩니다.

**Chart.yaml:**

```yaml
apiVersion: v2
name: common-lib
version: 0.1.0
description: Common library chart for shared templates
type: library    # library 타입으로 설정
```

**공통 템플릿 정의 (`templates/_deployment.tpl`):**

```yaml
{{/*
표준 Deployment 템플릿
사용법: {{ include "common.deployment" . }}
*/}}
{{- define "common.deployment" -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "common.fullname" . }}
  labels:
    {{- include "common.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "common.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "common.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: {{ .Values.service.port }}
{{- end }}
```

**라이브러리 차트 사용 (의존 차트에서):**

```yaml
# Chart.yaml
dependencies:
  - name: common-lib
    version: "0.1.0"
    repository: "file://../common-lib"
```

```yaml
# templates/deployment.yaml
{{ include "common.deployment" . }}
```

## .helmignore 설정

패키징 시 제외할 파일 패턴을 정의합니다. `.gitignore`와 동일한 문법입니다.

```
# .helmignore

# 개발용 파일
.DS_Store
.git/
.gitignore
.helmignore

# 개발 환경 values
values-dev.yaml
values-local.yaml

# CI/CD 설정
.github/
.gitlab-ci.yml
Makefile

# 문서
docs/
*.md
!README.md

# 테스트 파일
tests/
*_test.go

# 임시 파일
*.tmp
*.bak
```

## CRD 처리

`crds/` 디렉토리의 CRD는 일반 템플릿보다 먼저 설치되며, 업그레이드 시 자동 업데이트되지 않습니다.

```
crds/
└── my-crd.yaml    # 순수 CRD YAML (템플릿 문법 사용 불가)
```

**주의사항:**
- `crds/` 내 파일은 Go 템플릿 문법을 사용할 수 없습니다
- CRD 업그레이드는 `kubectl apply` 또는 별도 Job Hook으로 처리합니다
- CRD가 포함된 차트는 `--skip-crds` 플래그로 CRD 설치를 건너뛸 수 있습니다

```bash
# CRD 설치 건너뛰기 (이미 설치된 경우)
helm install my-release ./my-app --skip-crds
```
