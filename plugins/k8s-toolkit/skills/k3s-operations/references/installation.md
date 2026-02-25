# k3s 설치 가이드

## 단일 노드 설치

### 기본 설치

```bash
# 최신 안정 버전 설치
curl -sfL https://get.k3s.io | sh -

# 특정 버전 설치
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.29.4+k3s1 sh -

# 설치 완료 확인
systemctl status k3s
kubectl get nodes
```

### 설치 환경 변수 옵션

| 변수 | 설명 | 예시 |
|------|------|------|
| `INSTALL_K3S_VERSION` | 설치할 k3s 버전 | `v1.29.4+k3s1` |
| `INSTALL_K3S_EXEC` | k3s 실행 인자 | `server --disable traefik` |
| `INSTALL_K3S_CHANNEL` | 채널 선택 | `stable`, `latest`, `v1.29` |
| `INSTALL_K3S_SKIP_START` | 설치 후 자동 시작 건너뜀 | `true` |
| `K3S_TOKEN` | 클러스터 토큰 지정 | `mysecrettoken` |
| `K3S_KUBECONFIG_MODE` | kubeconfig 파일 권한 | `644` |

```bash
# 예시: Traefik 비활성화, kubeconfig 공개, 특정 버전
curl -sfL https://get.k3s.io | \
  INSTALL_K3S_VERSION=v1.29.4+k3s1 \
  INSTALL_K3S_EXEC="server --disable traefik --write-kubeconfig-mode 644" \
  sh -
```

### 설정 파일로 설치

설치 전에 `/etc/rancher/k3s/config.yaml`을 미리 생성하면 설치 시 자동으로 적용됩니다.

```yaml
# /etc/rancher/k3s/config.yaml
write-kubeconfig-mode: "0644"
disable:
  - traefik
  - servicelb
cluster-cidr: "10.42.0.0/16"
service-cidr: "10.43.0.0/16"
flannel-backend: "vxlan"
```

```bash
mkdir -p /etc/rancher/k3s
cat > /etc/rancher/k3s/config.yaml << 'EOF'
write-kubeconfig-mode: "0644"
disable:
  - traefik
EOF

curl -sfL https://get.k3s.io | sh -
```

## 에이전트 노드 추가

### 서버에서 토큰 확인

```bash
# 서버 노드에서 실행
cat /var/lib/rancher/k3s/server/node-token
# 출력 예: K10abc123...::server:xyz789...
```

### 에이전트 노드 설치

```bash
# 에이전트 노드에서 실행
curl -sfL https://get.k3s.io | \
  K3S_URL=https://<server-ip>:6443 \
  K3S_TOKEN=<node-token> \
  sh -

# 서비스 확인
systemctl status k3s-agent

# 서버에서 노드 확인
kubectl get nodes
```

### 에이전트 설정 파일

```yaml
# /etc/rancher/k3s/config.yaml (에이전트 노드)
server: "https://192.168.1.10:6443"
token: "K10abc123...::server:xyz789..."
node-label:
  - "role=worker"
  - "zone=us-east-1a"
node-taint:
  - "dedicated=gpu:NoSchedule"
```

## 주요 설치 옵션

### 컴포넌트 비활성화

```bash
# 개별 비활성화
curl -sfL https://get.k3s.io | sh -s - server \
  --disable traefik \
  --disable servicelb \
  --disable local-storage \
  --disable metrics-server

# 또는 config.yaml에서
disable:
  - traefik
  - servicelb
  - local-storage
  - metrics-server
```

비활성화 가능한 컴포넌트:
- `traefik` - Traefik Ingress Controller
- `servicelb` - ServiceLB (Klipper LoadBalancer)
- `local-storage` - Local Path Provisioner
- `metrics-server` - Metrics Server
- `coredns` - CoreDNS (직접 배포 시)

### 네트워크 설정

```bash
# CIDR 변경 (기본값: cluster-cidr=10.42.0.0/16, service-cidr=10.43.0.0/16)
--cluster-cidr 10.100.0.0/16
--service-cidr 10.101.0.0/16
--cluster-dns 10.101.0.10

# Flannel 백엔드 변경
--flannel-backend vxlan      # 기본값
--flannel-backend host-gw    # L2 네트워크 직접 라우팅 (성능 우수)
--flannel-backend wireguard  # 암호화 (성능 오버헤드 있음)
--flannel-backend none       # Flannel 비활성화 (커스텀 CNI 설치 시)
```

### TLS 설정

```bash
# SAN 추가 (로드밸런서 IP/도메인을 인증서에 포함)
--tls-san lb.example.com
--tls-san 192.168.1.100
```

HA 구성 또는 외부 접근 시 반드시 `--tls-san`을 설정합니다.

## 에어갭(Air-gap) 설치

인터넷이 차단된 환경에서의 설치 방법입니다.

### 필요 파일 준비 (인터넷 연결 가능한 머신에서)

```bash
# k3s 릴리즈 페이지에서 다운로드
# https://github.com/k3s-io/k3s/releases

VERSION=v1.29.4+k3s1

# k3s 바이너리
wget https://github.com/k3s-io/k3s/releases/download/${VERSION}/k3s

# 이미지 tarball (아키텍처에 맞게 선택)
wget https://github.com/k3s-io/k3s/releases/download/${VERSION}/k3s-airgap-images-amd64.tar.zst

# 설치 스크립트
wget https://get.k3s.io -O install.sh
```

### 에어갭 환경에 배포

```bash
# 바이너리 배포
sudo cp k3s /usr/local/bin/k3s
sudo chmod +x /usr/local/bin/k3s

# 이미지 tarball 배포
sudo mkdir -p /var/lib/rancher/k3s/agent/images/
sudo cp k3s-airgap-images-amd64.tar.zst /var/lib/rancher/k3s/agent/images/

# 설치 (오프라인 모드)
INSTALL_K3S_SKIP_DOWNLOAD=true bash install.sh
```

### 프라이빗 레지스트리 설정

```yaml
# /etc/rancher/k3s/registries.yaml
mirrors:
  "docker.io":
    endpoint:
      - "https://registry.example.com"
  "registry.k8s.io":
    endpoint:
      - "https://registry.example.com"

configs:
  "registry.example.com":
    auth:
      username: admin
      password: password
    tls:
      cert_file: /etc/ssl/certs/registry.crt
      key_file: /etc/ssl/certs/registry.key
      ca_file: /etc/ssl/certs/ca.crt
```

## systemd 서비스 설정

### 서비스 파일 위치

```
/etc/systemd/system/k3s.service          # 서버
/etc/systemd/system/k3s-agent.service    # 에이전트
/etc/systemd/system/k3s.service.env      # 환경 변수 파일
```

### 환경 변수 파일로 설정 관리

```bash
# /etc/systemd/system/k3s.service.env
K3S_TOKEN=mysecrettoken
K3S_KUBECONFIG_MODE=644
```

### 서비스 재시작 및 로그

```bash
# 서비스 관리
systemctl daemon-reload
systemctl restart k3s
systemctl stop k3s
systemctl enable k3s   # 부팅 시 자동 시작

# 로그 확인
journalctl -u k3s -f
journalctl -u k3s --since "1 hour ago"
journalctl -u k3s-agent -f
```

## 제거

### 서버 노드 제거

```bash
# k3s 서버 완전 제거 (컨테이너, 볼륨, CNI 설정 포함)
/usr/local/bin/k3s-uninstall.sh
```

### 에이전트 노드 제거

```bash
# k3s 에이전트 완전 제거
/usr/local/bin/k3s-agent-uninstall.sh
```

제거 스크립트는 다음을 수행합니다.
- k3s 서비스 중지 및 비활성화
- k3s 바이너리 및 관련 파일 삭제
- CNI 인터페이스 정리 (flannel.1, cni0 등)
- iptables 규칙 정리
- 마운트된 볼륨 언마운트 및 데이터 삭제

**주의**: 제거 스크립트는 `/var/lib/rancher/k3s/storage/` 데이터도 삭제합니다. 데이터 보존이 필요하면 미리 백업합니다.

## 멀티 아키텍처 지원

k3s는 다음 아키텍처를 지원합니다.

| 아키텍처 | 바이너리 이름 |
|----------|--------------|
| x86_64 | k3s |
| arm64 | k3s-arm64 |
| armhf | k3s-armhf |

Raspberry Pi와 같은 ARM 기기에서도 동일한 설치 방법을 사용합니다. 설치 스크립트가 아키텍처를 자동 감지합니다.
