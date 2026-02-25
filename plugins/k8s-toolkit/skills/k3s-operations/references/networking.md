# k3s 네트워킹 가이드

## Traefik Ingress Controller

k3s는 Traefik을 기본 Ingress Controller로 내장합니다. k3s v1.21+ 에서는 Traefik v2, v1.28+ 에서는 Traefik v3이 기본입니다.

### 기본 Ingress 설정

```yaml
# 표준 Kubernetes Ingress (Traefik 자동 처리)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  namespace: default
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web,websecure
spec:
  ingressClassName: traefik
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-service
                port:
                  number: 80
  tls:
    - hosts:
        - app.example.com
      secretName: app-tls-secret
```

### HelmChartConfig로 Traefik 커스터마이징

k3s는 `HelmChartConfig` CRD를 통해 내장 Helm 차트를 커스터마이징합니다.

```yaml
# /var/lib/rancher/k3s/server/manifests/traefik-config.yaml
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    # HTTPS 리다이렉트 활성화
    ports:
      web:
        redirectTo:
          port: websecure
    # 대시보드 활성화
    ingressRoute:
      dashboard:
        enabled: true
    # 실제 클라이언트 IP 전달
    service:
      spec:
        externalTrafficPolicy: Local
    # 로그 레벨
    logs:
      general:
        level: INFO
```

이 파일을 생성/수정하면 k3s가 자동으로 Traefik 설정을 업데이트합니다.

### Traefik 비활성화 후 다른 Ingress 사용

```bash
# Traefik 비활성화
curl -sfL https://get.k3s.io | sh -s - server --disable traefik

# nginx-ingress 설치
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

# 또는 Helm으로 설치
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer
```

### IngressRoute (Traefik CRD)

Traefik CRD를 사용하면 더 세밀한 라우팅 설정이 가능합니다.

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: my-app-route
  namespace: default
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`app.example.com`) && PathPrefix(`/api`)
      kind: Rule
      services:
        - name: api-service
          port: 8080
      middlewares:
        - name: rate-limit
  tls:
    certResolver: letsencrypt
```

## CoreDNS

### 기본 CoreDNS 설정 확인

```bash
# CoreDNS ConfigMap 확인
kubectl get configmap coredns -n kube-system -o yaml
```

### Corefile 커스터마이징

```yaml
# CoreDNS ConfigMap 수정
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        health {
           lameduck 5s
        }
        ready
        kubernetes cluster.local in-addr.arpa ip6.arpa {
          pods insecure
          fallthrough in-addr.arpa ip6.arpa
          ttl 30
        }
        prometheus :9153
        forward . 8.8.8.8 1.1.1.1 {
          max_concurrent 1000
        }
        cache 30
        loop
        reload
        loadbalance
    }
    # 커스텀 도메인 추가
    example.internal:53 {
        errors
        cache 30
        forward . 192.168.1.53
    }
```

### DNS 디버깅

```bash
# CoreDNS 파드 확인
kubectl get pods -n kube-system -l k8s-app=kube-dns

# DNS 해석 테스트 (디버그 파드)
kubectl run dns-test --image=busybox:latest --rm -it -- nslookup kubernetes.default
kubectl run dns-test --image=busybox:latest --rm -it -- nslookup my-service.default.svc.cluster.local

# CoreDNS 로그 확인
kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50
```

## ServiceLB (Klipper)

### 동작 방식

ServiceLB는 LoadBalancer 타입의 Service를 지원하기 위해 DaemonSet으로 실행됩니다. 각 노드에 svclb 파드가 생성되고 hostPort를 통해 트래픽을 전달합니다.

```bash
# ServiceLB 파드 확인
kubectl get pods -n kube-system -l svccontroller.k3s.cattle.io/svcname

# LoadBalancer Service IP 확인
kubectl get svc -A
```

### ServiceLB 동작 제한

- 하나의 포트는 노드당 하나의 서비스만 사용 가능합니다.
- 동일 포트를 사용하는 여러 LoadBalancer Service는 충돌이 발생합니다.
- 노드의 IP를 ExternalIP로 사용하므로 dedicated VIP가 필요하면 MetalLB를 사용합니다.

### ServiceLB 비활성화 후 MetalLB 설치

```bash
# ServiceLB 비활성화
# /etc/rancher/k3s/config.yaml에 추가
disable:
  - servicelb

# MetalLB 설치
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.5/config/manifests/metallb-native.yaml

# MetalLB IP 풀 설정
cat << EOF | kubectl apply -f -
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: first-pool
  namespace: metallb-system
spec:
  addresses:
    - 192.168.1.200-192.168.1.250
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: example
  namespace: metallb-system
spec:
  ipAddressPools:
    - first-pool
EOF
```

## Flannel CNI

### Flannel 백엔드 옵션

| 백엔드 | 성능 | 요구사항 | 사용 사례 |
|--------|------|----------|-----------|
| `vxlan` | 보통 | L3 라우팅 | 기본값, 대부분의 환경 |
| `host-gw` | 우수 | L2 동일 서브넷 | 고성능이 필요한 온프레미스 |
| `wireguard` | 보통 | wireguard 커널 모듈 | 암호화가 필요한 환경 |
| `none` | N/A | 커스텀 CNI 별도 설치 | Calico, Cilium 사용 시 |

```bash
# 백엔드 변경 (설치 시 또는 config.yaml)
flannel-backend: host-gw

# Flannel 인터페이스 확인
ip link show flannel.1
ip link show cni0
```

### 커스텀 CNI 설치 (Calico)

```bash
# Flannel 비활성화하고 Calico 설치
curl -sfL https://get.k3s.io | sh -s - server \
  --flannel-backend=none \
  --disable-network-policy \
  --cluster-cidr=192.168.0.0/16

# Calico 설치
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.0/manifests/tigera-operator.yaml

cat << EOF | kubectl apply -f -
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  calicoNetwork:
    ipPools:
      - blockSize: 26
        cidr: 192.168.0.0/16
        encapsulation: VXLANCrossSubnet
        natOutgoing: Enabled
        nodeSelector: all()
EOF
```

### 커스텀 CNI 설치 (Cilium)

```bash
# Flannel 비활성화
curl -sfL https://get.k3s.io | sh -s - server \
  --flannel-backend=none \
  --disable-network-policy

# Helm으로 Cilium 설치
helm repo add cilium https://helm.cilium.io/
helm install cilium cilium/cilium \
  --namespace kube-system \
  --set operator.replicas=1 \
  --set ipam.mode=kubernetes
```

## 네트워크 정책

### Flannel + NetworkPolicy (kube-router)

Flannel은 기본적으로 NetworkPolicy를 지원하지 않습니다. 네트워크 정책이 필요하면 kube-router를 추가로 설치합니다.

```bash
# kube-router 설치
kubectl apply -f https://raw.githubusercontent.com/cloudnativelabs/kube-router/master/daemonset/generic-kuberouter-only-advertise-routes.yaml
```

또는 Calico/Cilium으로 CNI를 교체하면 NetworkPolicy가 기본 지원됩니다.

### 기본 NetworkPolicy 예시

```yaml
# 기본 거부 정책
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
---
# 특정 트래픽만 허용
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-server
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
```

## 포트 요구사항

서버와 에이전트 간 방화벽에서 다음 포트를 허용합니다.

| 포트 | 프로토콜 | 방향 | 설명 |
|------|----------|------|------|
| 6443 | TCP | 에이전트 → 서버 | Kubernetes API |
| 8472 | UDP | 양방향 | Flannel VXLAN |
| 10250 | TCP | 서버 → 에이전트 | kubelet API |
| 51820 | UDP | 양방향 | Flannel WireGuard (IPv4) |
| 51821 | UDP | 양방향 | Flannel WireGuard (IPv6) |
| 2379-2380 | TCP | 서버 간 | etcd (HA 구성 시) |

```bash
# UFW 방화벽 설정 예시
ufw allow 6443/tcp
ufw allow 8472/udp
ufw allow 10250/tcp
ufw allow 2379:2380/tcp

# firewalld 설정 예시
firewall-cmd --permanent --add-port=6443/tcp
firewall-cmd --permanent --add-port=8472/udp
firewall-cmd --permanent --add-port=10250/tcp
firewall-cmd --reload
```
