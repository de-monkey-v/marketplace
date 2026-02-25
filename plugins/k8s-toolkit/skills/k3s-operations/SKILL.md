---
name: k3s-operations
description: "This skill should be used when the user asks to \"k3s 설치\", \"k3s 클러스터\", \"k3s 노드 추가\", \"경량 쿠버네티스\", \"k3s 운영\", \"k3s 업그레이드\", \"k3s 설정\", \"k3s troubleshoot\", or mentions k3s cluster installation, operation, or management. Provides guidance for k3s lightweight Kubernetes."
version: 0.1.0
---

# k3s 운영 가이드

k3s는 Rancher Labs(SUSE)에서 개발한 경량 Kubernetes 배포판입니다. IoT, Edge, 개발/테스트, 소규모 프로덕션 환경에 최적화되어 있습니다.

## k3s vs k8s 핵심 차이점

| 항목 | k3s | 표준 k8s |
|------|-----|----------|
| 바이너리 크기 | ~70MB 단일 바이너리 | 컴포넌트별 분리 |
| 메모리 요구량 | 서버 512MB / 에이전트 256MB | 서버 2GB+ / 워커 1GB+ |
| 기본 데이터스토어 | SQLite (단일 노드) | etcd |
| HA 데이터스토어 | 내장 etcd 또는 외부 DB | etcd |
| 컨테이너 런타임 | containerd (내장) | containerd / CRI-O |
| 네트워크 플러그인 | Flannel (내장) | 선택 설치 |
| Ingress | Traefik (내장) | 선택 설치 |
| LB | ServiceLB/Klipper (내장) | 선택 설치 |
| 스토리지 | local-path-provisioner (내장) | 선택 설치 |

### 경량화 요소

k3s는 다음 Kubernetes 컴포넌트를 제거 또는 통합하여 경량화를 달성합니다.

- alpha/deprecated API 제거
- 레거시 클라우드 프로바이더 코드 제거
- etcd → SQLite 기본값 (선택적 etcd 사용 가능)
- 모든 컨트롤 플레인 컴포넌트를 단일 프로세스로 통합

## 아키텍처 개요

### 서버(Control-Plane) 노드

k3s 서버 노드는 다음 컴포넌트를 단일 프로세스(`k3s server`)로 실행합니다.

- kube-apiserver
- kube-controller-manager
- kube-scheduler
- kube-proxy
- kubelet
- containerd
- Flannel (CNI)
- CoreDNS
- Traefik (Ingress)
- ServiceLB (Klipper)
- local-path-provisioner

### 에이전트(Worker) 노드

에이전트 노드는 `k3s agent`로 실행하며 다음만 포함합니다.

- kubelet
- kube-proxy
- containerd
- Flannel

## 내장 컴포넌트 요약

### Traefik Ingress Controller

버전에 따라 Traefik v2 또는 v3이 기본 설치됩니다. `HelmChartConfig` CRD로 커스터마이징합니다.

```yaml
# /var/lib/rancher/k3s/server/manifests/traefik-config.yaml
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    globalArguments: []
    service:
      spec:
        externalTrafficPolicy: Local
```

비활성화: `--disable traefik` 설치 옵션 사용.

### CoreDNS

k3s 내장 CoreDNS는 자동으로 배포되며, ConfigMap으로 커스터마이징합니다. 상세 설정은 [`references/networking.md`](references/networking.md) 참조.

### ServiceLB (Klipper)

LoadBalancer 타입 Service를 지원하는 내장 솔루션입니다. 서버 노드에서 DaemonSet으로 실행되며 hostPort를 사용합니다. 비활성화: `--disable servicelb`.

### Local Path Provisioner

기본 StorageClass(`local-path`)를 제공합니다. 기본 경로: `/var/lib/rancher/k3s/storage`. 상세 설정은 [`references/storage.md`](references/storage.md) 참조.

### Flannel

기본 CNI로 vxlan 백엔드를 사용합니다. wireguard, host-gw로 변경 가능합니다.

## 설치 전 체크리스트

설치 전 다음 항목을 확인합니다.

```
[ ] OS: Ubuntu 20.04+, Debian 11+, CentOS 7+, Rocky Linux 8+
[ ] 최소 리소스: CPU 1코어, RAM 512MB (서버), 256MB (에이전트)
[ ] 포트 개방: 6443(API), 10250(kubelet), 8472/UDP(Flannel vxlan)
[ ] 스왑 비활성화: swapoff -a (권장, 필수는 아님)
[ ] 방화벽 규칙 확인 (firewalld / ufw)
[ ] 시스템 시간 동기화 확인 (NTP)
[ ] 고유 호스트명 설정 (멀티 노드 시 필수)
```

## 설치 후 체크리스트

설치 완료 후 다음 항목을 검증합니다.

```
[ ] 서비스 상태: systemctl status k3s
[ ] 노드 상태: kubectl get nodes
[ ] 시스템 파드 상태: kubectl get pods -n kube-system
[ ] kubeconfig 권한: /etc/rancher/k3s/k3s.yaml (root 전용)
[ ] 노드 토큰 확인: /var/lib/rancher/k3s/server/node-token
```

## 노드 구성 원칙

### 서버/에이전트 분리

- 서버 노드는 컨트롤 플레인 역할에 집중합니다. 워크로드는 에이전트 노드에 배치합니다.
- 서버 노드에 워크로드를 배치하려면 taint를 제거합니다.
- 프로덕션에서는 서버 노드를 taint하여 워크로드 혼용을 방지합니다.

```bash
# 서버 노드에 워크로드 배치 방지 (taint 추가)
kubectl taint nodes <server-node> node-role.kubernetes.io/control-plane:NoSchedule

# 서버 노드에서도 워크로드 실행 허용 (taint 제거)
kubectl taint nodes <server-node> node-role.kubernetes.io/control-plane:NoSchedule-
```

### 리소스 요구사항 (권장)

| 역할 | CPU | RAM | 디스크 |
|------|-----|-----|--------|
| 서버 (개발) | 2코어 | 2GB | 20GB |
| 서버 (프로덕션) | 4코어 | 4GB | 50GB |
| 에이전트 | 2코어 | 2GB | 30GB+ |
| HA 서버 (최소 3대) | 2코어 | 4GB | 50GB |

### 설정 파일 위치

k3s 서버와 에이전트 설정은 `/etc/rancher/k3s/config.yaml`에서 관리합니다.

```yaml
# /etc/rancher/k3s/config.yaml (서버 예시)
write-kubeconfig-mode: "0644"
tls-san:
  - "lb.example.com"
  - "192.168.1.100"
disable:
  - traefik
cluster-cidr: "10.42.0.0/16"
service-cidr: "10.43.0.0/16"
```

## 주요 디렉토리/파일 위치

| 경로 | 설명 |
|------|------|
| `/etc/rancher/k3s/config.yaml` | k3s 설정 파일 |
| `/etc/rancher/k3s/k3s.yaml` | kubeconfig |
| `/var/lib/rancher/k3s/server/node-token` | 노드 조인 토큰 |
| `/var/lib/rancher/k3s/server/manifests/` | 자동 배포 매니페스트 |
| `/var/lib/rancher/k3s/storage/` | local-path 스토리지 |
| `/var/lib/rancher/k3s/server/db/` | SQLite/etcd 데이터 |
| `/usr/local/bin/k3s` | k3s 바이너리 |
| `/usr/local/bin/k3s-uninstall.sh` | 서버 제거 스크립트 |
| `/usr/local/bin/k3s-agent-uninstall.sh` | 에이전트 제거 스크립트 |

## 기본 운영 명령어

```bash
# 상태 확인
systemctl status k3s
kubectl get nodes -o wide
kubectl get pods -A

# kubeconfig 설정 (일반 사용자)
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
# 또는 홈 디렉토리로 복사
cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
chmod 600 ~/.kube/config

# crictl 사용 (컨테이너 직접 디버깅)
crictl ps
crictl images
crictl logs <container-id>

# k3s 내장 kubectl/crictl
k3s kubectl get nodes
k3s crictl ps
```

## 참고 자료

### Reference Files

- **[`references/installation.md`](references/installation.md)** - k3s 설치 가이드 (단일 노드, 멀티 노드, 에어갭, 설정 옵션)
- **[`references/networking.md`](references/networking.md)** - k3s 네트워킹 (Traefik, CoreDNS, Flannel, ServiceLB, 커스텀 CNI)
- **[`references/storage.md`](references/storage.md)** - k3s 스토리지 (Local Path, Longhorn, NFS, StorageClass)
- **[`references/ha-cluster.md`](references/ha-cluster.md)** - 고가용성 구성 (내장 etcd HA, 외부 DB, 로드밸런서)
- **[`references/troubleshooting.md`](references/troubleshooting.md)** - 트러블슈팅 (로그 확인, 일반 문제, 인증서, 네트워크)
- **[`references/upgrades.md`](references/upgrades.md)** - 업그레이드/롤백 (버전 업그레이드, 자동 업그레이드, 롤백)
