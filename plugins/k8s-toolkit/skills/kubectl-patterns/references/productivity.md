# 생산성 도구

kubectl 작업 효율을 높이는 alias, 자동완성, 플러그인, 도구들을 다룹니다.

## Alias 설정

### 기본 alias

`.bashrc` 또는 `.zshrc`에 추가합니다.

```bash
# 기본 단축키
alias k='kubectl'
alias kk='kubectl -n kube-system'

# Get 명령어
alias kgp='kubectl get pods'
alias kgpa='kubectl get pods --all-namespaces'
alias kgs='kubectl get svc'
alias kgsa='kubectl get svc --all-namespaces'
alias kgd='kubectl get deployment'
alias kgda='kubectl get deployment --all-namespaces'
alias kgn='kubectl get nodes'
alias kgns='kubectl get namespaces'
alias kgcm='kubectl get configmap'
alias kgsec='kubectl get secret'
alias kgpv='kubectl get pv'
alias kgpvc='kubectl get pvc'
alias kging='kubectl get ingress'

# Describe
alias kdp='kubectl describe pod'
alias kdn='kubectl describe node'
alias kds='kubectl describe svc'
alias kdd='kubectl describe deployment'

# 로그
alias kl='kubectl logs'
alias klf='kubectl logs -f'
alias klp='kubectl logs --previous'

# 적용/삭제
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
alias kdel='kubectl delete'

# 실행
alias kex='kubectl exec -it'

# 컨텍스트
alias kctx='kubectl config use-context'
alias kns='kubectl config set-context --current --namespace'
```

### 고급 함수

```bash
# 파드 이름 자동완성 exec
kexec() {
  kubectl exec -it "$1" -- ${2:-/bin/sh}
}

# 특정 라벨의 첫 번째 파드에 접속
kexl() {
  local pod=$(kubectl get pods -l "$1" -o jsonpath='{.items[0].metadata.name}')
  kubectl exec -it "$pod" -- ${2:-/bin/sh}
}

# 파드 로그 (라벨로 첫 번째 파드 선택)
klabel() {
  local pod=$(kubectl get pods -l "$1" -o jsonpath='{.items[0].metadata.name}')
  kubectl logs -f "$pod"
}

# 네임스페이스 내 모든 리소스 조회
kall() {
  kubectl get all -n "${1:-default}"
}

# 파드를 재시작 (디플로이먼트 롤아웃)
krestart() {
  kubectl rollout restart deployment/"$1"
}
```

## 자동완성 설정

### Bash

```bash
# kubectl 자동완성 활성화
source <(kubectl completion bash)

# .bashrc에 영구 추가
echo 'source <(kubectl completion bash)' >> ~/.bashrc

# alias와 자동완성 함께 사용
alias k=kubectl
complete -o default -F __start_kubectl k
```

### Zsh

```bash
# kubectl 자동완성 활성화
source <(kubectl completion zsh)

# .zshrc에 영구 추가
echo 'source <(kubectl completion zsh)' >> ~/.zshrc

# Oh-My-Zsh 플러그인 사용 (권장)
# plugins=(... kubectl)
# .zshrc의 plugins 배열에 kubectl 추가

# alias와 자동완성
alias k='kubectl'
compdef k=kubectl
```

## Kustomize

kubectl에 내장된 선언적 설정 관리 도구입니다.

### 기본 kustomization.yaml

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - deployment.yaml
  - service.yaml
  - configmap.yaml

namespace: my-namespace

commonLabels:
  app: myapp
  team: backend

images:
  - name: myapp
    newTag: v2.1.0
```

### Kustomize Overlays 패턴

```
base/
├── kustomization.yaml
├── deployment.yaml
└── service.yaml

overlays/
├── development/
│   ├── kustomization.yaml    # base 참조 + dev 변경사항
│   └── patch-replicas.yaml
├── staging/
│   ├── kustomization.yaml
│   └── patch-resources.yaml
└── production/
    ├── kustomization.yaml
    └── patch-production.yaml
```

```yaml
# overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

namespace: production

images:
  - name: myapp
    newTag: v2.1.0

patches:
  - path: patch-production.yaml
    target:
      kind: Deployment
      name: myapp
```

### Kustomize 명령어

```bash
# 변환된 YAML 미리보기
kubectl kustomize ./overlays/production

# 적용
kubectl apply -k ./overlays/production

# 특정 오버레이 적용
kubectl apply -k ./overlays/development

# 삭제
kubectl delete -k ./overlays/staging

# diff 확인
kubectl diff -k ./overlays/production
```

## dry-run과 diff 활용

```bash
# 클라이언트 사이드 dry-run (API 서버 호출 없음)
kubectl apply -f deployment.yaml --dry-run=client

# 서버 사이드 dry-run (유효성 완전 검증)
kubectl apply -f deployment.yaml --dry-run=server

# 현재 클러스터 상태와 차이 확인
kubectl diff -f deployment.yaml

# 디렉토리 전체 diff
kubectl diff -f ./manifests/

# kustomize와 함께 diff
kubectl diff -k ./overlays/production

# YAML 출력하여 확인
kubectl apply -f deployment.yaml --dry-run=client -o yaml
```

## krew - kubectl 플러그인 관리자

### krew 설치

```bash
# Linux/macOS
(
  set -x; cd "$(mktemp -d)" &&
  OS="$(uname | tr '[:upper:]' '[:lower:]')" &&
  ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/\(arm\)\(64\)\?.*/\1\2/' -e 's/aarch64$/arm64/')" &&
  KREW="krew-${OS}_${ARCH}" &&
  curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" &&
  tar zxvf "${KREW}.tar.gz" &&
  ./"${KREW}" install krew
)

# PATH 추가 (.bashrc/.zshrc)
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"
```

### 유용한 krew 플러그인

```bash
# 플러그인 검색
kubectl krew search
kubectl krew search ctx

# 플러그인 설치
kubectl krew install ctx         # 컨텍스트 전환
kubectl krew install ns          # 네임스페이스 전환
kubectl krew install neat        # YAML 깔끔하게 출력
kubectl krew install tree        # 리소스 트리 구조 보기
kubectl krew install who-can     # RBAC 권한 조회
kubectl krew install access-matrix  # 권한 매트릭스
kubectl krew install tail        # 멀티 파드 로그
kubectl krew install stern       # 멀티 파드 로그 (권장)
kubectl krew install node-shell  # 노드에 직접 쉘
kubectl krew install view-secret # 시크릿 디코딩 조회
kubectl krew install konfig      # kubeconfig 병합
kubectl krew install images      # 파드 이미지 목록

# 플러그인 업데이트
kubectl krew upgrade

# 설치된 플러그인 목록
kubectl krew list
```

### 주요 플러그인 사용법

```bash
# neat: 불필요한 필드 제거하여 깔끔한 YAML 출력
kubectl get deployment my-app -o yaml | kubectl neat

# tree: 리소스 소유 관계 트리 보기
kubectl tree deployment my-app

# who-can: 특정 작업 가능한 사용자 조회
kubectl who-can get pods
kubectl who-can delete deployments -n production

# access-matrix: 네임스페이스별 권한 매트릭스
kubectl access-matrix --namespace production

# view-secret: 시크릿 자동 디코딩
kubectl view-secret my-secret
kubectl view-secret my-secret password

# node-shell: 노드에 직접 접속
kubectl node-shell my-node

# images: 모든 파드의 이미지 목록
kubectl images
kubectl images -n production
```

## stern - 멀티 파드 로그

여러 파드의 로그를 동시에 스트리밍합니다.

### 설치

```bash
# brew (macOS)
brew install stern

# krew
kubectl krew install stern

# 바이너리 직접 다운로드
# https://github.com/stern/stern/releases
```

### 사용법

```bash
# 이름 패턴으로 파드 로그
stern myapp

# 특정 네임스페이스
stern myapp -n production

# 전체 네임스페이스
stern myapp -A

# 라벨 셀렉터
stern -l app=myapp

# 최근 1시간 로그
stern myapp --since 1h

# 정규식 필터 (포함)
stern myapp --include "ERROR|WARN"

# 정규식 필터 (제외)
stern myapp --exclude "health-check"

# 특정 컨테이너 로그
stern myapp -c app

# 타임스탬프 형식 지정
stern myapp --timestamps

# 출력 형식 커스터마이징
stern myapp --output raw

# 색상 없이 출력 (파일 저장 시)
stern myapp --color never > app.log
```

## k9s - 터미널 UI

터미널 기반의 Kubernetes 대시보드입니다.

### 설치

```bash
# brew (macOS)
brew install k9s

# 바이너리 다운로드
# https://github.com/derailed/k9s/releases

# snap (Linux)
sudo snap install k9s
```

### 기본 사용법

```bash
# k9s 실행
k9s

# 특정 네임스페이스로 시작
k9s -n production

# 특정 컨텍스트로 시작
k9s --context prod-cluster

# 읽기 전용 모드
k9s --readonly
```

### k9s 키보드 단축키

```
:pods          파드 뷰로 이동
:deploy        디플로이먼트 뷰
:svc           서비스 뷰
:ns            네임스페이스 뷰
:nodes         노드 뷰

l              선택한 파드 로그
e              리소스 편집
d              describe
Ctrl+d         삭제
s              쉘 접속 (exec)
Ctrl+k         강제 종료
/              검색/필터
?              키 도움말
Esc            이전 화면
:q             종료
```

## 유용한 원라이너

```bash
# 모든 파드의 이미지 목록
kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.metadata.name}{"\t"}{range .spec.containers[*]}{.image}{" "}{end}{"\n"}{end}'

# Failed/Evicted 파드 정리
kubectl delete pods -A --field-selector status.phase=Failed
kubectl get pods -A | grep Evicted | awk '{print $1" "$2}' | xargs -L1 kubectl delete pod -n

# CrashLoopBackOff 파드 목록
kubectl get pods -A | grep CrashLoopBackOff

# 재시작 횟수가 5회 이상인 파드
kubectl get pods -A -o jsonpath='{range .items[?(@.status.containerStatuses[0].restartCount>5)]}{.metadata.namespace}{"\t"}{.metadata.name}{"\t"}{.status.containerStatuses[0].restartCount}{"\n"}{end}'

# 리소스 requests/limits 없는 파드 찾기
kubectl get pods -A -o json | jq -r '.items[] | select(.spec.containers[0].resources.requests == null) | "\(.metadata.namespace)\t\(.metadata.name)"'

# 특정 이미지를 사용하는 파드 찾기
kubectl get pods -A -o json | jq -r '.items[] | select(.spec.containers[].image | contains("nginx")) | "\(.metadata.namespace)\t\(.metadata.name)"'

# 노드별 파드 수
kubectl get pods -A -o wide --no-headers | awk '{print $8}' | sort | uniq -c | sort -rn

# 만료 예정인 시크릿 확인 (TLS)
kubectl get secrets -A -o json | jq -r '.items[] | select(.type=="kubernetes.io/tls") | "\(.metadata.namespace)\t\(.metadata.name)\t\(.data["tls.crt"])" | @base64d' 2>/dev/null

# 모든 디플로이먼트 재시작 (네임스페이스 내)
kubectl rollout restart deployment -n production

# Pending 파드 이유 요약
kubectl get pods -A --field-selector status.phase=Pending -o json | \
  jq -r '.items[] | "\(.metadata.namespace)/\(.metadata.name): \(.status.conditions[] | select(.type=="PodScheduled") | .message)"'
```

## 환경변수 활용

```bash
# 기본 네임스페이스 설정 (kubectl config 없이)
export KUBECTL_DEFAULT_NAMESPACE=production

# kubeconfig 파일 지정
export KUBECONFIG=~/.kube/prod-config

# 에디터 설정
export KUBE_EDITOR=vim
export KUBE_EDITOR="code --wait"

# kubectl 출력에 색상 비활성화
export NO_COLOR=1
```
