# k3s 트러블슈팅 가이드

## 로그 확인

### k3s 서비스 로그

```bash
# 실시간 로그
journalctl -u k3s -f

# 최근 100줄
journalctl -u k3s -n 100

# 시간 범위 지정
journalctl -u k3s --since "2024-01-01 10:00" --until "2024-01-01 12:00"

# 에이전트 로그
journalctl -u k3s-agent -f

# 오류만 필터링
journalctl -u k3s -p err -n 50
```

### 파드/컨테이너 로그

```bash
# 파드 로그
kubectl logs <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --previous  # 이전 컨테이너 로그
kubectl logs <pod-name> -n <namespace> -c <container-name>  # 멀티 컨테이너

# 시스템 파드 로그
kubectl logs -n kube-system -l k8s-app=kube-dns     # CoreDNS
kubectl logs -n kube-system -l app.kubernetes.io/name=traefik  # Traefik

# crictl로 컨테이너 로그 직접 확인
crictl ps -a
crictl logs <container-id>
```

## 노드 문제

### 노드 NotReady

```bash
# 노드 상태 및 조건 확인
kubectl get nodes
kubectl describe node <node-name>

# 주요 확인 사항:
# - Conditions 섹션의 Ready, MemoryPressure, DiskPressure, PIDPressure
# - Events 섹션의 최근 이벤트

# 노드 kubelet 상태
# (서버 노드는 k3s, 에이전트 노드는 k3s-agent)
systemctl status k3s
systemctl status k3s-agent

# 노드 리소스 확인
kubectl top nodes  # metrics-server 필요

# 노드에서 직접 디스크/메모리 확인
df -h
free -h
```

**일반적인 원인과 해결책:**

| 원인 | 증상 | 해결 |
|------|------|------|
| 디스크 용량 부족 | DiskPressure | 불필요한 이미지 정리: `crictl rmi --prune` |
| 메모리 부족 | MemoryPressure | 불필요한 파드 제거, 노드 리소스 증가 |
| 네트워크 단절 | 에이전트 → 서버 연결 불가 | 방화벽/네트워크 설정 확인 |
| k3s 프로세스 크래시 | systemd service 실패 | `systemctl restart k3s-agent`, 로그 확인 |

### 노드 강제 재등록

```bash
# 에이전트 노드에서
systemctl stop k3s-agent
rm -rf /var/lib/rancher/k3s/agent/etc/
systemctl start k3s-agent
```

## 파드 문제

### Pod CrashLoopBackOff

```bash
# 파드 상태 상세 확인
kubectl describe pod <pod-name> -n <namespace>

# 이전 컨테이너 로그 확인 (크래시 직전 로그)
kubectl logs <pod-name> -n <namespace> --previous

# 이벤트 확인
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# 파드를 쉘로 디버깅 (디버그 이미지 사용)
kubectl debug -it <pod-name> --image=busybox --copy-to=debug-pod
```

**일반적인 원인:**
- 애플리케이션 설정 오류 → 환경 변수, ConfigMap, Secret 확인
- OOMKilled → 메모리 limits 증가
- 이미지 오류 → `kubectl describe pod`에서 이미지 풀 실패 확인
- liveness probe 실패 → probe 경로/포트/지연 시간 확인

### 이미지 풀 실패 (ImagePullBackOff)

```bash
# 상세 오류 확인
kubectl describe pod <pod-name>
# Events: Failed to pull image... unauthorized / not found / timeout

# 프라이빗 레지스트리 인증
kubectl create secret docker-registry regcred \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=password \
  --docker-email=user@example.com

# Pod spec에 imagePullSecrets 추가
spec:
  imagePullSecrets:
    - name: regcred

# crictl로 이미지 직접 풀 테스트
crictl pull registry.example.com/myimage:latest
```

### Pod Pending (스케줄링 불가)

```bash
# 스케줄링 실패 이유 확인
kubectl describe pod <pod-name>
# Events: 0/3 nodes are available: ...

# 노드 리소스 확인
kubectl describe nodes | grep -A 5 "Allocated resources"

# Taint/toleration 확인
kubectl get nodes -o json | jq '.items[].spec.taints'

# 노드 셀렉터/어피니티 확인
kubectl get pod <pod-name> -o yaml | grep -A 10 "nodeSelector\|affinity"
```

## DNS 문제

### DNS 해석 실패

```bash
# CoreDNS 파드 상태 확인
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl describe pod -n kube-system -l k8s-app=kube-dns

# CoreDNS 로그 확인
kubectl logs -n kube-system -l k8s-app=kube-dns

# DNS 해석 테스트
kubectl run dns-test --image=busybox:latest --rm -it --restart=Never -- \
  nslookup kubernetes.default.svc.cluster.local

# 서비스 DNS 테스트
kubectl run dns-test --image=busybox:latest --rm -it --restart=Never -- \
  nslookup <service-name>.<namespace>.svc.cluster.local

# CoreDNS ConfigMap 확인
kubectl get configmap coredns -n kube-system -o yaml
```

**일반적인 원인:**
- CoreDNS 파드 미실행 → 재시작: `kubectl rollout restart deployment coredns -n kube-system`
- 잘못된 DNS 설정 → CoreDNS ConfigMap 확인
- 파드 /etc/resolv.conf 설정 확인: `kubectl exec <pod> -- cat /etc/resolv.conf`

## 네트워크 문제

### 파드 간 통신 불가

```bash
# Flannel 파드 상태 확인
kubectl get pods -n kube-system -l app=flannel

# CNI 인터페이스 상태 확인
ip link show flannel.1
ip link show cni0

# 파드 IP 및 라우팅 확인
kubectl get pods -o wide -A
ip route show

# 파드 간 ping 테스트
kubectl exec -it <pod1> -- ping <pod2-ip>

# iptables 규칙 확인
iptables -L FORWARD --line-numbers
iptables -t nat -L -n
```

**일반적인 원인:**
- Flannel 인터페이스 손상 → 노드 재시작 또는 `ip link delete flannel.1`
- iptables 규칙 충돌 → `iptables -F && iptables -X` (주의: 일시적으로 모든 연결 차단)
- 방화벽이 8472/UDP 차단 → 방화벽 규칙 확인

### 서비스 접근 불가

```bash
# 서비스 엔드포인트 확인
kubectl get endpoints <service-name>
kubectl describe service <service-name>

# 서비스 선택자와 파드 라벨 일치 확인
kubectl get pods -l <selector-key>=<selector-value>

# iptables 서비스 규칙 확인
iptables -t nat -L KUBE-SERVICES -n | grep <service-cluster-ip>

# kube-proxy 대신 사용되는 k3s의 kube-proxy 상태
kubectl get pods -n kube-system | grep kube-proxy
```

### Ingress 동작 안함

```bash
# Traefik 파드 상태
kubectl get pods -n kube-system -l app.kubernetes.io/name=traefik
kubectl describe pod -n kube-system -l app.kubernetes.io/name=traefik

# Traefik 로그
kubectl logs -n kube-system -l app.kubernetes.io/name=traefik --tail=50

# Ingress 리소스 확인
kubectl get ingress -A
kubectl describe ingress <ingress-name>

# Traefik 설정 확인 (대시보드)
kubectl port-forward -n kube-system svc/traefik 9000:9000
# http://localhost:9000/dashboard/

# IngressClass 확인
kubectl get ingressclass
```

## 인증서 문제

### 인증서 만료 확인

```bash
# k3s 인증서 만료일 확인
for cert in /var/lib/rancher/k3s/server/tls/*.crt; do
  echo "=== $cert ==="
  openssl x509 -in "$cert" -noout -dates 2>/dev/null
done

# kubeconfig 인증서 확인
kubectl config view --raw | grep certificate-authority-data | awk '{print $2}' | base64 -d | openssl x509 -noout -dates
```

### 인증서 로테이션

```bash
# k3s 인증서 수동 로테이션
systemctl stop k3s
k3s certificate rotate
systemctl start k3s

# 또는 자동 로테이션 활성화 (config.yaml)
# k3s는 기본적으로 90일 이내에 만료되는 인증서를 자동 갱신
```

### --tls-san 누락 문제

```bash
# 인증서에 포함된 SAN 확인
openssl x509 -in /var/lib/rancher/k3s/server/tls/serving-kube-apiserver.crt -noout -text | grep -A 5 "Subject Alternative Name"

# SAN 추가 (서버 재시작 필요)
# /etc/rancher/k3s/config.yaml에 추가
tls-san:
  - "new-lb.example.com"
  - "203.0.113.10"

# 인증서 재생성
systemctl stop k3s
rm /var/lib/rancher/k3s/server/tls/serving-kube-apiserver.*
systemctl start k3s
```

## 스토리지 문제

### PVC Pending

```bash
# PVC 상태 확인
kubectl get pvc -A
kubectl describe pvc <pvc-name>

# StorageClass 확인
kubectl get storageclass
kubectl describe storageclass <storage-class-name>

# Provisioner 파드 상태 확인
kubectl get pods -n kube-system | grep local-path
kubectl logs -n kube-system -l app=local-path-provisioner
```

**일반적인 원인:**
- StorageClass 미존재 → `kubectl get storageclass` 확인
- 노드 디스크 부족 → `df -h` 확인
- Provisioner 파드 오류 → Provisioner 로그 확인

### 볼륨 마운트 실패

```bash
# 파드 이벤트 확인
kubectl describe pod <pod-name>
# Events: Unable to mount volumes...

# 마운트 포인트 확인 (노드에서)
mount | grep <pvc-name>

# 강제 언마운트 (주의)
umount -f -l /var/lib/rancher/k3s/storage/<pvc-dir>
```

## 디버깅 도구

### crictl 명령어

```bash
# 컨테이너 목록
crictl ps -a

# 이미지 목록
crictl images

# 파드 목록
crictl pods

# 컨테이너 로그
crictl logs <container-id>

# 컨테이너 exec
crictl exec -it <container-id> sh

# 이미지 정리
crictl rmi --prune

# 디스크 사용량
crictl stats
```

### k3s 내장 진단 도구

```bash
# k3s 설정 검증
k3s check-config

# etcd 스냅샷 목록
k3s etcd-snapshot ls

# k3s 버전 확인
k3s --version
kubectl version

# 클러스터 정보
kubectl cluster-info
kubectl get componentstatuses
```

### 진단 정보 수집 스크립트

```bash
#!/bin/bash
# k3s 진단 정보 수집
OUTDIR="/tmp/k3s-diag-$(date +%Y%m%d%H%M%S)"
mkdir -p "$OUTDIR"

# 노드 정보
kubectl get nodes -o wide > "$OUTDIR/nodes.txt"
kubectl describe nodes > "$OUTDIR/nodes-describe.txt"

# 파드 정보
kubectl get pods -A -o wide > "$OUTDIR/pods.txt"
kubectl get events -A --sort-by='.lastTimestamp' > "$OUTDIR/events.txt"

# 시스템 파드
kubectl get pods -n kube-system -o wide > "$OUTDIR/system-pods.txt"

# k3s 로그 (최근 1000줄)
journalctl -u k3s -n 1000 > "$OUTDIR/k3s.log"

# 시스템 리소스
free -h > "$OUTDIR/memory.txt"
df -h > "$OUTDIR/disk.txt"
top -bn1 > "$OUTDIR/top.txt"

echo "진단 정보 수집 완료: $OUTDIR"
tar -czf "$OUTDIR.tar.gz" "$OUTDIR"
echo "압축 파일: $OUTDIR.tar.gz"
```
