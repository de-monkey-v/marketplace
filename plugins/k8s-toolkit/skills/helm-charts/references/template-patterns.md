# Go 템플릿 패턴 가이드

Helm 템플릿은 Go의 `text/template` 패키지를 기반으로 하며, Sprig 함수 라이브러리와 Helm 전용 함수를 추가로 제공합니다.

## Go Template 기본 문법

### 기본 구분자

```yaml
# 값 출력
{{ .Values.image.repository }}

# 공백 제거 (왼쪽)
{{- .Values.image.repository }}

# 공백 제거 (오른쪽)
{{ .Values.image.repository -}}

# 양쪽 공백 제거
{{- .Values.image.repository -}}
```

### 공백 제어

공백 제어는 YAML 들여쓰기에 중요합니다:

```yaml
# 나쁨: 불필요한 빈 줄 생성
metadata:
  name: {{ .Release.Name }}

  labels:
    {{ include "my-app.labels" . | nindent 4 }}

# 좋음: 깔끔한 렌더링
metadata:
  name: {{ .Release.Name }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
```

## 내장 객체

```yaml
# Release 객체
.Release.Name          # 릴리스 이름
.Release.Namespace     # 네임스페이스
.Release.IsInstall     # 설치 여부 (bool)
.Release.IsUpgrade     # 업그레이드 여부 (bool)
.Release.Service       # "Helm"

# Chart 객체
.Chart.Name            # 차트 이름
.Chart.Version         # 차트 버전
.Chart.AppVersion      # 앱 버전
.Chart.Description     # 차트 설명

# Values 객체
.Values.image.repository    # values.yaml 값 접근

# Files 객체
.Files.Get "config.yaml"    # 파일 내용 읽기
.Files.Glob "configs/*"     # 파일 목록

# Capabilities 객체
.Capabilities.KubeVersion.Major    # k8s 주 버전
.Capabilities.APIVersions.Has "apps/v1"  # API 버전 확인
```

## 핵심 함수

### include / template

```yaml
# include: 출력을 파이프라인으로 전달 가능 (권장)
labels:
  {{- include "my-app.labels" . | nindent 4 }}

# template: 직접 출력 (파이프라인 불가)
{{- template "my-app.labels" . }}
```

### required

필수 값이 없으면 오류를 발생시킵니다:

```yaml
host: {{ required "database.host must be provided" .Values.database.host | quote }}
```

### default

기본값을 제공합니다:

```yaml
# 값이 비어있을 때 기본값 사용
tag: {{ .Values.image.tag | default .Chart.AppVersion | quote }}
replicas: {{ .Values.replicaCount | default 1 }}
logLevel: {{ .Values.config.logLevel | default "info" | quote }}
```

### toYaml / indent / nindent

복잡한 YAML 구조를 안전하게 포함합니다:

```yaml
# nindent: 들여쓰기 포함 줄바꿈 추가 (가장 많이 사용)
{{- with .Values.resources }}
resources:
  {{- toYaml . | nindent 2 }}
{{- end }}

# indent: 들여쓰기만 추가 (줄바꿈 없음)
resources:
  {{ toYaml .Values.resources | indent 2 }}
```

### tpl 함수

values.yaml 내 문자열을 동적 템플릿으로 렌더링합니다:

```yaml
# values.yaml
config:
  message: "Hello, {{ .Release.Name }}!"

# templates/configmap.yaml
data:
  message: {{ tpl .Values.config.message . | quote }}
# 결과: message: "Hello, my-release!"
```

## 조건부 렌더링

### if / else / else if

```yaml
# 기본 조건
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
...
{{- end }}

# else 분기
{{- if eq .Values.service.type "LoadBalancer" }}
  type: LoadBalancer
{{- else if eq .Values.service.type "NodePort" }}
  type: NodePort
{{- else }}
  type: ClusterIP
{{- end }}

# 복합 조건
{{- if and .Values.ingress.enabled .Values.ingress.tls }}
  tls:
    {{- toYaml .Values.ingress.tls | nindent 4 }}
{{- end }}

# not 조건
{{- if not .Values.serviceAccount.create }}
  serviceAccountName: default
{{- end }}
```

### with

값이 존재할 때만 블록 실행하고 스코프를 변경합니다:

```yaml
# with: 값이 비어있지 않을 때만 실행
{{- with .Values.nodeSelector }}
nodeSelector:
  {{- toYaml . | nindent 2 }}
{{- end }}

{{- with .Values.tolerations }}
tolerations:
  {{- toYaml . | nindent 2 }}
{{- end }}

{{- with .Values.affinity }}
affinity:
  {{- toYaml . | nindent 2 }}
{{- end }}

# with 블록 내부에서 $.Values로 루트 접근
{{- with .Values.ingress }}
  {{- range .hosts }}
  - host: {{ .host | quote }}
    paths:
    {{- range .paths }}
      - path: {{ .path }}
        # $.Release.Namespace로 루트 접근
        # namespace: {{ $.Release.Namespace }}
    {{- end }}
  {{- end }}
{{- end }}
```

## 반복문

### range (리스트 순회)

```yaml
# 인덱스와 값
{{- range $i, $port := .Values.service.extraPorts }}
- name: port-{{ $i }}
  containerPort: {{ $port }}
{{- end }}

# 값만
{{- range .Values.imagePullSecrets }}
- name: {{ .name }}
{{- end }}

# 문자열 슬라이스
{{- range .Values.args }}
- {{ . | quote }}
{{- end }}
```

### range (맵 순회)

```yaml
# 키와 값
{{- range $key, $value := .Values.podAnnotations }}
{{ $key }}: {{ $value | quote }}
{{- end }}

# 환경변수 맵 처리
env:
{{- range $key, $value := .Values.env }}
  - name: {{ $key | upper }}
    value: {{ $value | quote }}
{{- end }}
```

## 파이프라인

함수를 체이닝하여 복잡한 변환을 수행합니다:

```yaml
# 문자열 변환
{{ .Values.app.name | lower | replace " " "-" | trunc 63 | trimSuffix "-" }}

# 따옴표 처리
{{ .Values.config.logLevel | quote }}           # "info"
{{ .Values.image.tag | default "latest" | quote }}

# 숫자 처리
{{ .Values.replicaCount | int }}
{{ .Values.service.port | toString | quote }}

# JSON/YAML 변환
{{ .Values.config | toJson }}
{{ .Values.resources | toYaml | nindent 4 }}

# 체크섬 (ConfigMap 변경 감지)
annotations:
  checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

## ConfigMap에서 파일 내용 로드

```yaml
# templates/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "my-app.fullname" . }}-config
data:
  # .Files.Get으로 파일 내용 로드
  nginx.conf: |-
    {{ .Files.Get "files/nginx.conf" | nindent 4 }}

  # 바이너리 파일 (base64 인코딩)
  {{- (.Files.Glob "files/certs/*").AsSecrets | nindent 2 }}
```

## 실전 Deployment 템플릿

완전한 Deployment 템플릿 예시:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-app.fullname" . }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "my-app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        # ConfigMap 변경 시 Pod 재시작
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "my-app.selectorLabels" . | nindent 8 }}
        {{- with .Values.podLabels }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "my-app.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort | default 8080 }}
              protocol: TCP
          {{- with .Values.livenessProbe }}
          livenessProbe:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with .Values.readinessProbe }}
          readinessProbe:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          {{- with .Values.volumeMounts }}
          volumeMounts:
            {{- toYaml . | nindent 12 }}
          {{- end }}
      {{- with .Values.volumes }}
      volumes:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

## 디버깅

```bash
# 템플릿 렌더링 결과 확인 (클러스터 불필요)
helm template my-release ./my-app \
  --values values-dev.yaml \
  --debug

# 특정 템플릿만 렌더링
helm template my-release ./my-app \
  --show-only templates/deployment.yaml

# 클러스터에 드라이런 (API 서버 검증 포함)
helm install my-release ./my-app \
  --dry-run \
  --debug \
  --generate-name

# 템플릿 내 디버그 출력 (렌더링 결과에 주석으로 출력)
{{- /* 디버그: {{ .Values | toYaml }} */ -}}
```

### 일반적인 오류 해결

```bash
# YAML 들여쓰기 오류 확인
helm template . | kubectl apply --dry-run=client -f -

# 특정 값 확인
helm get values my-release

# 현재 배포된 매니페스트 확인
helm get manifest my-release
```
