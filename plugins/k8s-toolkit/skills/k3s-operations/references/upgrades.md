# k3s 업그레이드/롤백 가이드

## 버전 체계 이해

k3s 버전은 Kubernetes 버전과 k3s 패치 버전으로 구성됩니다.

```
v1.29.4+k3s1
│  │  │  │
│  │  │  └── k3s 패치 버전
│  │  └───── Kubernetes 패치 버전
│  └──────── Kubernetes 마이너 버전
└─────────── Kubernetes 메이저 버전
```

**버전 호환성:**

| k3s 버전 | Kubernetes 버전 |
|----------|----------------|
| v1.30.x+k3sN | v1.30.x |
| v1.29.x+k3sN | v1.29.x |
| v1.28.x+k3sN | v1.28.x |

## 수동 업그레이드

### 사전 준비

```bash
# 현재 버전 확인
k3s --version
kubectl version

# 업그레이드할 버전 결정
# GitHub Releases: https://github.com/k3s-io/k3s/releases
# 권장: 마이너 버전 하나씩 업그레이드 (예: 1.27 → 1.28 → 1.29)

# 클러스터 현재 상태 확인
kubectl get nodes
kubectl get pods -A | grep -v Running | grep -v Completed
```

### 서버 노드 업그레이드

```bash
# 1. 업그레이드 전 etcd 스냅샷 백업
k3s etcd-snapshot save --name pre-upgrade-$(date +%Y%m%d%H%M%S)

# 2. 서버 노드 워크로드 이동 (선택사항, 트래픽 있는 경우)
kubectl cordon <server-node>
kubectl drain <server-node> --ignore-daemonsets --delete-emptydir-data

# 3. k3s 업그레이드 (install 스크립트가 기존 설치를 덮어씀)
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.30.0+k3s1 sh -

# 4. 서비스 재시작 확인
systemctl status k3s

# 5. 노드 버전 확인
kubectl get nodes

# 6. 노드 복귀 (cordon한 경우)
kubectl uncordon <server-node>
```

### 에이전트 노드 업그레이드

서버 노드 업그레이드 완료 후 에이전트 노드를 순차 업그레이드합니다.

```bash
# 1. 에이전트 노드 워크로드 이동
kubectl cordon <agent-node>
kubectl drain <agent-node> --ignore-daemonsets --delete-emptydir-data

# 2. 에이전트 노드에서 실행
curl -sfL https://get.k3s.io | \
  INSTALL_K3S_VERSION=v1.30.0+k3s1 \
  K3S_URL=https://<server-ip>:6443 \
  K3S_TOKEN=<token> \
  sh -

# 3. 에이전트 서비스 확인
systemctl status k3s-agent

# 4. 노드 복귀
kubectl uncordon <agent-node>

# 5. 파드 정상 확인 후 다음 에이전트 진행
kubectl get pods -o wide | grep <agent-node>
```

### HA 클러스터 업그레이드 순서

```
1. etcd 스냅샷 백업
2. 서버1 업그레이드 (cordon → drain → upgrade → uncordon)
3. 서버1 정상 확인
4. 서버2 업그레이드
5. 서버2 정상 확인
6. 서버3 업그레이드
7. 서버3 정상 확인
8. 에이전트 노드들 순차 업그레이드
```

**주의:** HA 환경에서 서버 노드를 동시에 업그레이드하면 etcd 쿼럼이 깨져 클러스터가 다운될 수 있습니다.

## system-upgrade-controller 자동 업그레이드

Rancher의 system-upgrade-controller를 사용하면 Kubernetes CRD(`Plan`)로 자동 업그레이드를 선언적으로 관리합니다.

### system-upgrade-controller 설치

```bash
kubectl apply -f https://github.com/rancher/system-upgrade-controller/releases/latest/download/system-upgrade-controller.yaml
kubectl apply -f https://github.com/rancher/system-upgrade-controller/releases/latest/download/crd.yaml

# 설치 확인
kubectl get pods -n system-upgrade
```

### 서버 노드 업그레이드 Plan

```yaml
# server-plan.yaml
apiVersion: upgrade.cattle.io/v1
kind: Plan
metadata:
  name: server-plan
  namespace: system-upgrade
spec:
  concurrency: 1  # 동시에 업그레이드할 노드 수
  cordon: true    # 업그레이드 전 cordon
  nodeSelector:
    matchExpressions:
      - key: node-role.kubernetes.io/control-plane
        operator: In
        values:
          - "true"
  serviceAccountName: system-upgrade
  tolerations:
    - key: CriticalAddonsOnly
      operator: Exists
  upgrade:
    image: rancher/k3s-upgrade
  channel: https://update.k3s.io/v1-release/channels/stable
  # 또는 특정 버전 지정
  # version: v1.30.0+k3s1
```

### 에이전트 노드 업그레이드 Plan

```yaml
# agent-plan.yaml
apiVersion: upgrade.cattle.io/v1
kind: Plan
metadata:
  name: agent-plan
  namespace: system-upgrade
spec:
  concurrency: 2    # 에이전트는 여러 개 동시 업그레이드 가능
  cordon: true
  nodeSelector:
    matchExpressions:
      - key: node-role.kubernetes.io/control-plane
        operator: DoesNotExist
  prepare:
    # 서버 플랜이 완료된 후 에이전트 플랜 시작
    args:
      - prepare
      - server-plan
    image: rancher/k3s-upgrade
  serviceAccountName: system-upgrade
  upgrade:
    image: rancher/k3s-upgrade
  channel: https://update.k3s.io/v1-release/channels/stable
```

```bash
# 업그레이드 Plan 적용
kubectl apply -f server-plan.yaml
kubectl apply -f agent-plan.yaml

# 업그레이드 진행 상태 확인
kubectl get plans -n system-upgrade
kubectl get jobs -n system-upgrade
kubectl get pods -n system-upgrade

# 노드 업그레이드 상태
kubectl get nodes
```

### 업그레이드 채널

| 채널 URL | 설명 |
|----------|------|
| `https://update.k3s.io/v1-release/channels/stable` | 안정 채널 (권장) |
| `https://update.k3s.io/v1-release/channels/latest` | 최신 채널 |
| `https://update.k3s.io/v1-release/channels/v1.29` | 특정 마이너 버전 채널 |

## 롤백

### 이전 버전으로 재설치

```bash
# 이전 버전 k3s 재설치 (데이터는 보존)
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.29.4+k3s1 sh -
systemctl restart k3s

# 버전 확인
k3s --version
```

### etcd 스냅샷으로 롤백

업그레이드 후 심각한 문제가 발생한 경우 스냅샷으로 복원합니다.

```bash
# 1. 스냅샷 목록 확인
k3s etcd-snapshot ls

# 2. 이전 버전 k3s 재설치
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.29.4+k3s1 sh -

# 3. k3s 중지
systemctl stop k3s

# 4. 스냅샷 복원 (--cluster-reset 사용)
k3s server \
  --cluster-reset \
  --cluster-reset-restore-path=/var/lib/rancher/k3s/server/db/snapshots/pre-upgrade-20240101120000

# 5. k3s 재시작
systemctl start k3s

# 6. 클러스터 상태 확인
kubectl get nodes
kubectl get pods -A
```

## 무중단 업그레이드 절차 (상세)

프로덕션 환경에서 서비스 중단 없이 업그레이드하는 절차입니다.

```bash
# 함수 정의
upgrade_node() {
  local NODE=$1
  local VERSION=$2

  echo "=== $NODE 업그레이드 시작 ==="

  # 1. cordon (새 파드 스케줄링 방지)
  kubectl cordon "$NODE"

  # 2. drain (기존 파드 이동)
  kubectl drain "$NODE" \
    --ignore-daemonsets \
    --delete-emptydir-data \
    --grace-period=60 \
    --timeout=5m

  echo "$NODE drain 완료. 업그레이드를 진행하세요."
  echo "업그레이드 완료 후 Enter를 누르세요..."
  read

  # 3. 업그레이드 완료 후 복귀
  kubectl uncordon "$NODE"

  # 4. 파드 복귀 확인 (최대 5분 대기)
  echo "$NODE 파드 복귀 대기 중..."
  kubectl wait --for=condition=Ready pod -l app=my-app --timeout=300s

  echo "=== $NODE 업그레이드 완료 ==="
}

# 서버 노드 순차 업그레이드
upgrade_node server1 v1.30.0+k3s1
upgrade_node server2 v1.30.0+k3s1
upgrade_node server3 v1.30.0+k3s1

# 에이전트 노드 순차 업그레이드
for AGENT in agent1 agent2 agent3; do
  upgrade_node "$AGENT" v1.30.0+k3s1
done
```

## 체인지로그 및 호환성 확인

업그레이드 전 항상 릴리즈 노트를 확인합니다.

```bash
# GitHub Releases 확인
# https://github.com/k3s-io/k3s/releases

# 현재 사용 중인 Kubernetes API 확인 (deprecated API 체크)
kubectl get --raw /apis | python3 -m json.tool | grep "apiVersion"

# deprecated API 사용 체크 도구 (pluto)
helm install pluto fairwinds-stable/pluto
kubectl run pluto --image=us-docker.pkg.dev/fairwinds-ops/oss/pluto:latest --rm -it -- \
  detect-all-in-cluster
```

**업그레이드 권장 사항:**
- 마이너 버전은 한 번에 하나씩 업그레이드합니다 (1.27 → 1.28 → 1.29, 1.27 → 1.29 건너뛰기 비권장).
- 업그레이드 전 etcd 스냅샷을 항상 생성합니다.
- 스테이징 환경에서 먼저 업그레이드를 검증합니다.
- 서버 노드를 모두 업그레이드한 후 에이전트를 업그레이드합니다.
- 에이전트는 서버보다 한 마이너 버전 낮은 버전을 유지할 수 있습니다.
