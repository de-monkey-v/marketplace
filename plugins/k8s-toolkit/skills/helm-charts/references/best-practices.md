# 프로덕션 모범 사례

프로덕션 환경에서 Helm 차트를 안전하고 안정적으로 운영하기 위한 전략과 패턴입니다.

## 차트 릴리스 전략

### helm upgrade --install 패턴

설치와 업그레이드를 단일 명령으로 처리하는 idempotent 패턴:

```bash
helm upgrade --install my-app ./my-app \
  --namespace production \
  --create-namespace \
  --values values.yaml \
  --values values-prod.yaml \
  --set image.tag=$IMAGE_TAG \
  --atomic \            # 실패 시 자동 롤백
  --wait \              # 모든 Pod Ready 대기
  --timeout 10m \       # 대기 시간 제한
  --cleanup-on-fail     # 실패 시 새로 생성된 리소스 정리
```

### --atomic vs --wait

| 옵션 | 동작 |
|------|------|
| `--wait` | 리소스가 Ready 상태가 될 때까지 대기 |
| `--atomic` | `--wait` + 실패 시 자동 롤백 |
| `--timeout` | 대기 시간 제한 (기본 5m) |

### 릴리스 이력 관리

```bash
# 릴리스 이력 확인
helm history my-app --namespace production

# 이전 버전으로 롤백
helm rollback my-app 3 --namespace production

# 최대 이력 수 제한
helm upgrade --install my-app ./my-app \
  --history-max 10    # 최근 10개만 유지
```

## 보안 하드닝

### RBAC 기본 포함

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
automountServiceAccountToken: false  # 기본적으로 토큰 마운트 비활성화
{{- end }}
```

```yaml
# templates/role.yaml
{{- if .Values.rbac.create }}
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {{ include "my-app.fullname" . }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
rules:
  {{- toYaml .Values.rbac.rules | nindent 2 }}
{{- end }}
```

### securityContext 기본값 설정

```yaml
# values.yaml - 보안 기본값
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 2000
  seccompProfile:
    type: RuntimeDefault

securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL
  seccompProfile:
    type: RuntimeDefault
```

### NetworkPolicy 포함

```yaml
# templates/networkpolicy.yaml
{{- if .Values.networkPolicy.enabled }}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{ include "my-app.fullname" . }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
spec:
  podSelector:
    matchLabels:
      {{- include "my-app.selectorLabels" . | nindent 6 }}
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        {{- if .Values.networkPolicy.ingressNSMatchLabels }}
        - namespaceSelector:
            matchLabels:
              {{- toYaml .Values.networkPolicy.ingressNSMatchLabels | nindent 14 }}
        {{- end }}
        - podSelector:
            matchLabels:
              {{- include "my-app.selectorLabels" . | nindent 14 }}
      ports:
        - protocol: TCP
          port: {{ .Values.service.targetPort | default 8080 }}
  egress:
    - {}  # 모든 외부 트래픽 허용 (필요에 따라 제한)
{{- end }}
```

### Pod Disruption Budget

```yaml
# templates/pdb.yaml
{{- if .Values.podDisruptionBudget.enabled }}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ include "my-app.fullname" . }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
spec:
  {{- if .Values.podDisruptionBudget.minAvailable }}
  minAvailable: {{ .Values.podDisruptionBudget.minAvailable }}
  {{- end }}
  {{- if .Values.podDisruptionBudget.maxUnavailable }}
  maxUnavailable: {{ .Values.podDisruptionBudget.maxUnavailable }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "my-app.selectorLabels" . | nindent 6 }}
{{- end }}
```

## CI/CD 통합

### 검증 파이프라인

```bash
#!/bin/bash
# ci/validate-chart.sh

set -e

CHART_DIR="${1:-.}"

echo "=== Helm Lint ==="
helm lint "$CHART_DIR" \
  --values "$CHART_DIR/values.yaml" \
  --values "$CHART_DIR/values-prod.yaml" \
  --strict

echo "=== Template Rendering ==="
helm template my-release "$CHART_DIR" \
  --values "$CHART_DIR/values-prod.yaml" \
  --debug > /tmp/rendered.yaml

echo "=== Kubernetes Schema Validation ==="
# kubeconform 설치 필요: https://github.com/yannh/kubeconform
kubeconform \
  --strict \
  --ignore-missing-schemas \
  --kubernetes-version "1.29.0" \
  /tmp/rendered.yaml

echo "All validations passed!"
```

### GitHub Actions 예시

```yaml
# .github/workflows/helm-ci.yml
name: Helm Chart CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Set up Helm
        uses: azure/setup-helm@v3
        with:
          version: v3.12.0

      - name: Set up chart-testing
        uses: helm/chart-testing-action@v2.6.0

      - name: Run chart-testing (lint)
        run: ct lint --config ct.yaml

      - name: Create kind cluster
        uses: helm/kind-action@v1.8.0
        if: steps.list-changed.outputs.changed == 'true'

      - name: Run chart-testing (install)
        run: ct install --config ct.yaml
        if: steps.list-changed.outputs.changed == 'true'
```

### chart-testing 설정

```yaml
# ct.yaml
remote: origin
target-branch: main
chart-dirs:
  - charts
chart-repos:
  - bitnami=https://charts.bitnami.com/bitnami
helm-extra-args: --timeout 600s
validate-maintainers: false
```

## GitOps 통합

### ArgoCD Application

```yaml
# argocd/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://charts.example.com
    chart: my-app
    targetRevision: 1.2.3
    helm:
      releaseName: my-app
      valueFiles:
        - values-prod.yaml
      values: |
        image:
          tag: "2.5.1"
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
```

### Flux HelmRelease

```yaml
# flux/helmrelease.yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: my-app
  namespace: production
spec:
  interval: 10m
  chart:
    spec:
      chart: my-app
      version: ">=1.0.0 <2.0.0"
      sourceRef:
        kind: HelmRepository
        name: my-charts
        namespace: flux-system
  values:
    replicaCount: 3
    image:
      tag: "2.5.1"
  upgrade:
    remediation:
      retries: 3
  rollback:
    cleanupOnFail: true
```

## 차트 배포

### GitHub Pages Helm 레포지토리

```bash
# 차트 패키징
helm package ./my-app --destination ./dist

# 레포지토리 인덱스 생성/갱신
helm repo index ./dist \
  --url https://myorg.github.io/helm-charts

# GitHub Pages로 배포 (gh-pages 브랜치)
```

### OCI 레지스트리로 배포

```bash
# 차트 패키징
helm package ./my-app

# OCI 레지스트리 로그인
helm registry login ghcr.io -u $GITHUB_ACTOR -p $GITHUB_TOKEN

# OCI 레지스트리에 푸시
helm push my-app-1.0.0.tgz oci://ghcr.io/myorg/charts
```

## 디버깅 명령어

```bash
# 현재 배포된 매니페스트 확인
helm get manifest my-release --namespace production

# 현재 적용된 values 확인
helm get values my-release --namespace production
helm get values my-release --namespace production --all  # 기본값 포함

# Hook 리소스 확인
helm get hooks my-release --namespace production

# 릴리스 상태 확인
helm status my-release --namespace production

# 릴리스 이력 확인
helm history my-release --namespace production

# 변경 사항 미리 보기 (helm-diff 플러그인)
helm diff upgrade my-release ./my-app \
  --values values-prod.yaml \
  --set image.tag=2.0.0
```

### helm-diff 플러그인 설치

```bash
helm plugin install https://github.com/databus23/helm-diff
```

## 프로덕션 배포 전 체크리스트

**차트 검증:**
- `helm lint --strict` 통과
- `helm template` 렌더링 오류 없음
- `kubeconform` 스키마 검증 통과
- `values.schema.json` 정의 완료

**보안:**
- `podSecurityContext` 설정 (`runAsNonRoot: true`)
- `securityContext` 설정 (`allowPrivilegeEscalation: false`)
- `resources` requests/limits 설정
- Secrets 평문 저장 없음

**고가용성:**
- `replicaCount >= 2` (프로덕션)
- `PodDisruptionBudget` 설정
- `livenessProbe` / `readinessProbe` 설정
- `affinity` 또는 `topologySpreadConstraints` 설정

**운영성:**
- `NOTES.txt` 유용한 안내 포함
- Hook으로 DB 마이그레이션 자동화
- `helm test` 작성
- 릴리스 이력 최대값 설정 (`--history-max`)
