# kubeconfig 관리

kubectl 컨텍스트와 kubeconfig 파일 관리 패턴을 다룹니다.

## kubeconfig 구조

kubeconfig 파일은 세 가지 핵심 요소로 구성됩니다.

```yaml
# ~/.kube/config
apiVersion: v1
kind: Config

clusters:                          # 클러스터 목록
- cluster:
    certificate-authority-data: DATA
    server: https://k8s.example.com:6443
  name: production-cluster
- cluster:
    server: https://staging.example.com:6443
  name: staging-cluster

users:                             # 인증 정보 목록
- name: admin-user
  user:
    client-certificate-data: DATA
    client-key-data: DATA
- name: dev-user
  user:
    token: eyJhbGciOiJSUzI1NiJ9...

contexts:                          # 클러스터 + 유저 + 네임스페이스 조합
- context:
    cluster: production-cluster
    user: admin-user
    namespace: default
  name: prod-admin
- context:
    cluster: staging-cluster
    user: dev-user
    namespace: development
  name: staging-dev

current-context: prod-admin        # 현재 활성 컨텍스트
```

## kubectl config 명령어

### 컨텍스트 조회

```bash
# 전체 컨텍스트 목록 (현재 컨텍스트에 * 표시)
kubectl config get-contexts

# 현재 컨텍스트 확인
kubectl config current-context

# kubeconfig 전체 내용 확인
kubectl config view

# 민감 정보 포함하여 전체 확인
kubectl config view --flatten
```

출력 예시:
```
CURRENT   NAME           CLUSTER            AUTHINFO   NAMESPACE
*         prod-admin     production-cluster admin-user default
          staging-dev    staging-cluster    dev-user   development
```

### 컨텍스트 전환

```bash
# 컨텍스트 전환
kubectl config use-context staging-dev

# 전환 후 확인
kubectl config current-context

# 일시적으로 다른 컨텍스트 사용 (전환 없이)
kubectl --context=staging-dev get pods
```

### 컨텍스트 생성/수정

```bash
# 새 컨텍스트 생성
kubectl config set-context my-context \
  --cluster=my-cluster \
  --user=my-user \
  --namespace=my-namespace

# 현재 컨텍스트의 기본 네임스페이스 변경
kubectl config set-context --current --namespace=production

# 컨텍스트 삭제
kubectl config delete-context old-context
```

### 클러스터/유저 관리

```bash
# 클러스터 정보 추가
kubectl config set-cluster my-cluster \
  --server=https://k8s.example.com:6443 \
  --certificate-authority=/path/to/ca.crt

# 인증 정보 추가 (토큰 기반)
kubectl config set-credentials my-user \
  --token=eyJhbGciOiJSUzI1NiJ9...

# 인증 정보 추가 (인증서 기반)
kubectl config set-credentials my-user \
  --client-certificate=/path/to/client.crt \
  --client-key=/path/to/client.key

# 클러스터 삭제
kubectl config delete-cluster old-cluster

# 유저 삭제
kubectl config delete-user old-user
```

## 다중 클러스터 관리

### KUBECONFIG 환경변수로 파일 병합

```bash
# 여러 kubeconfig 파일 동시 사용 (콜론으로 구분)
export KUBECONFIG=~/.kube/config:~/.kube/prod-config:~/.kube/staging-config

# 병합된 컨텍스트 목록 확인
kubectl config get-contexts

# 특정 파일 지정
kubectl --kubeconfig=/path/to/custom-config get pods
```

### kubeconfig 파일 병합

```bash
# 두 파일 병합하여 새 파일 생성
KUBECONFIG=~/.kube/config:~/.kube/new-cluster-config \
  kubectl config view --flatten > ~/.kube/merged-config

# 백업 후 교체
cp ~/.kube/config ~/.kube/config.backup
mv ~/.kube/merged-config ~/.kube/config
```

### 클러스터별 kubeconfig 관리

```bash
# 클러스터별로 별도 파일 관리
mkdir -p ~/.kube/clusters
# ~/.kube/clusters/production.yaml
# ~/.kube/clusters/staging.yaml
# ~/.kube/clusters/development.yaml

# .bashrc/.zshrc에 추가
export KUBECONFIG=$(find ~/.kube/clusters -name "*.yaml" | tr '\n' ':')$HOME/.kube/config
```

## kubectx/kubens - 빠른 전환

[kubectx/kubens](https://github.com/ahmetb/kubectx)를 설치하면 더 빠르게 전환할 수 있습니다.

### 설치

```bash
# brew 설치 (macOS)
brew install kubectx

# krew로 설치
kubectl krew install ctx
kubectl krew install ns

# Linux 수동 설치
sudo git clone https://github.com/ahmetb/kubectx /opt/kubectx
sudo ln -s /opt/kubectx/kubectx /usr/local/bin/kubectx
sudo ln -s /opt/kubectx/kubens /usr/local/bin/kubens
```

### kubectx 사용

```bash
# 컨텍스트 목록 (fzf 설치 시 대화형 선택)
kubectx

# 특정 컨텍스트로 전환
kubectx production

# 이전 컨텍스트로 돌아가기
kubectx -

# 컨텍스트 이름 변경
kubectx new-name=old-name

# 컨텍스트 삭제
kubectx -d old-context
```

### kubens 사용

```bash
# 네임스페이스 목록 (fzf 설치 시 대화형 선택)
kubens

# 특정 네임스페이스로 전환
kubens production

# 이전 네임스페이스로 돌아가기
kubens -
```

## fzf 연동 (대화형 선택)

fzf를 설치하면 kubectx/kubens가 대화형 선택 모드로 동작합니다.

```bash
# fzf 설치
brew install fzf        # macOS
apt-get install fzf     # Ubuntu

# kubectl 자체도 fzf 연동 가능
# .bashrc/.zshrc에 추가:
# 컨텍스트 선택
kctx() {
  kubectl config use-context $(kubectl config get-contexts -o name | fzf)
}

# 네임스페이스 선택
kns() {
  kubectl config set-context --current --namespace=$(kubectl get namespaces -o name | sed 's/namespace\///' | fzf)
}
```

## 보안 고려사항

### kubeconfig 파일 권한

```bash
# kubeconfig 파일 권한 제한 (본인만 읽기/쓰기)
chmod 600 ~/.kube/config

# 소유자 확인
ls -la ~/.kube/config

# 디렉토리 권한 확인
ls -la ~/.kube/
```

### ServiceAccount 토큰 기반 접근

```bash
# ServiceAccount 생성
kubectl create serviceaccount my-sa -n my-namespace

# ClusterRoleBinding 생성
kubectl create clusterrolebinding my-sa-binding \
  --clusterrole=view \
  --serviceaccount=my-namespace:my-sa

# 토큰 생성 (Kubernetes 1.24+)
kubectl create token my-sa -n my-namespace

# 영구 토큰 시크릿 생성 (1.24+ 에서는 비권장)
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: my-sa-token
  namespace: my-namespace
  annotations:
    kubernetes.io/service-account.name: my-sa
type: kubernetes.io/service-account-token
EOF

# 토큰 추출
kubectl get secret my-sa-token -n my-namespace \
  -o jsonpath='{.data.token}' | base64 --decode

# kubeconfig에 ServiceAccount 토큰 추가
TOKEN=$(kubectl create token my-sa -n my-namespace)
kubectl config set-credentials my-sa-user --token=$TOKEN
```

### RBAC 권한 확인

```bash
# 현재 사용자 권한 확인
kubectl auth can-i get pods
kubectl auth can-i delete deployments
kubectl auth can-i '*' '*'  # 모든 권한 확인

# 특정 사용자/ServiceAccount 권한 확인
kubectl auth can-i get pods --as=my-user
kubectl auth can-i get pods --as=system:serviceaccount:my-namespace:my-sa

# 전체 네임스페이스에서 권한 확인
kubectl auth can-i list pods -A

# kubectl krew plugin: who-can
kubectl who-can get pods
kubectl who-can create deployments -n production
```

## EKS/GKE/AKS kubeconfig 설정

### AWS EKS

```bash
# EKS 클러스터 kubeconfig 추가
aws eks update-kubeconfig --name my-cluster --region ap-northeast-2

# 특정 프로파일 사용
aws eks update-kubeconfig --name my-cluster --region ap-northeast-2 --profile my-profile

# kubeconfig 별칭 지정
aws eks update-kubeconfig --name my-cluster --region ap-northeast-2 --alias eks-prod
```

### GCP GKE

```bash
# GKE 클러스터 kubeconfig 추가
gcloud container clusters get-credentials my-cluster --zone asia-northeast3-a

# 특정 프로젝트 지정
gcloud container clusters get-credentials my-cluster \
  --zone asia-northeast3-a \
  --project my-project
```

### Azure AKS

```bash
# AKS 클러스터 kubeconfig 추가
az aks get-credentials --resource-group my-rg --name my-cluster

# 관리자 자격증명 (admin kubeconfig)
az aks get-credentials --resource-group my-rg --name my-cluster --admin
```
