# k3s 고가용성(HA) 구성 가이드

## HA 아키텍처 개요

k3s HA는 두 가지 방식으로 구성합니다.

1. **내장 etcd HA**: 별도 외부 DB 없이 etcd를 서버 노드에 내장
2. **외부 DB HA**: MySQL, PostgreSQL, 외부 etcd 사용

**프로덕션 권장 아키텍처:**

```
[로드밸런서 (HAProxy/Nginx)]
         |
    ─────┼─────
    |         |
[서버1]  [서버2]  [서버3]  ← 최소 3대 (홀수 권장)
    |         |
    ─────┼─────
         |
[에이전트1] [에이전트2] ... [에이전트N]
```

## 내장 etcd HA 구성

etcd가 k3s 서버 프로세스에 내장되어 별도 설치 없이 HA 클러스터를 구성합니다.

### 1단계: 첫 번째 서버 노드 초기화

```bash
# 첫 번째 서버에서 실행 (--cluster-init 필수)
curl -sfL https://get.k3s.io | sh -s - server \
  --cluster-init \
  --tls-san lb.example.com \
  --tls-san 192.168.1.100 \
  --token mysecrettoken

# 클러스터 초기화 확인
kubectl get nodes
systemctl status k3s
```

`--cluster-init`은 오직 첫 번째 서버에서만 한 번 사용합니다.

### 2단계: 추가 서버 노드 조인

```bash
# 두 번째, 세 번째 서버에서 실행 (--server 플래그)
curl -sfL https://get.k3s.io | sh -s - server \
  --server https://192.168.1.10:6443 \
  --tls-san lb.example.com \
  --tls-san 192.168.1.100 \
  --token mysecrettoken

# 두 번째 서버 조인 후 노드 상태 확인
kubectl get nodes
```

### config.yaml로 HA 서버 설정

```yaml
# /etc/rancher/k3s/config.yaml (두 번째, 세 번째 서버용)
server: "https://192.168.1.10:6443"
token: "<YOUR_K3S_TOKEN>"
tls-san:
  - "lb.example.com"
  - "192.168.1.100"
write-kubeconfig-mode: "0644"
disable:
  - traefik
```

### 3단계: 에이전트 노드 조인

```bash
# 에이전트는 로드밸런서를 통해 조인
curl -sfL https://get.k3s.io | \
  K3S_URL=https://lb.example.com:6443 \
  K3S_TOKEN=<YOUR_K3S_TOKEN> \
  sh -
```

### etcd 클러스터 상태 확인

```bash
# etcd 멤버 확인
k3s etcd-snapshot ls

# etcd 엔드포인트 상태
ETCDCTL_ENDPOINTS='https://127.0.0.1:2379' \
ETCDCTL_CACERT='/var/lib/rancher/k3s/server/tls/etcd/server-ca.crt' \
ETCDCTL_CERT='/var/lib/rancher/k3s/server/tls/etcd/client.crt' \
ETCDCTL_KEY='/var/lib/rancher/k3s/server/tls/etcd/client.key' \
ETCDCTL_API=3 etcdctl endpoint status --cluster -w table
```

## 외부 DB HA 구성

### MySQL/MariaDB 사용

```bash
# MySQL 데이터베이스 및 사용자 생성 (MySQL 서버에서)
mysql -u root -p << EOF
CREATE DATABASE k3s;
CREATE USER 'k3s'@'%' IDENTIFIED BY 'k3spassword';
GRANT ALL PRIVILEGES ON k3s.* TO 'k3s'@'%';
FLUSH PRIVILEGES;
EOF

# k3s 서버 설치 (datastore-endpoint 지정)
curl -sfL https://get.k3s.io | sh -s - server \
  --datastore-endpoint="mysql://k3s:k3spassword@tcp(192.168.1.20:3306)/k3s" \
  --tls-san lb.example.com \
  --token mysecrettoken
```

### PostgreSQL 사용

```bash
# PostgreSQL 설정
psql -U postgres << EOF
CREATE DATABASE k3s;
CREATE USER k3s WITH PASSWORD 'k3spassword';
GRANT ALL PRIVILEGES ON DATABASE k3s TO k3s;
EOF

# k3s 서버 설치
curl -sfL https://get.k3s.io | sh -s - server \
  --datastore-endpoint="postgres://k3s:k3spassword@192.168.1.20:5432/k3s" \
  --tls-san lb.example.com \
  --token mysecrettoken
```

### 외부 etcd 사용

```bash
# 외부 etcd 사용 시
curl -sfL https://get.k3s.io | sh -s - server \
  --datastore-endpoint="https://192.168.1.21:2379" \
  --datastore-cafile /etc/etcd/ca.crt \
  --datastore-certfile /etc/etcd/client.crt \
  --datastore-keyfile /etc/etcd/client.key \
  --tls-san lb.example.com \
  --token mysecrettoken
```

## 로드밸런서 구성

### HAProxy 설정

```bash
# HAProxy 설치
apt-get install -y haproxy

# /etc/haproxy/haproxy.cfg
cat > /etc/haproxy/haproxy.cfg << 'EOF'
global
    log /dev/log local0
    maxconn 4096

defaults
    log     global
    mode    tcp
    option  tcplog
    timeout connect 5000ms
    timeout client  50000ms
    timeout server  50000ms

frontend k3s-frontend
    bind *:6443
    default_backend k3s-backend

backend k3s-backend
    balance roundrobin
    option tcp-check
    server server1 192.168.1.10:6443 check
    server server2 192.168.1.11:6443 check
    server server3 192.168.1.12:6443 check
EOF

systemctl restart haproxy
systemctl enable haproxy
```

### Nginx 로드밸런서 설정

```nginx
# /etc/nginx/nginx.conf
stream {
    upstream k3s_servers {
        server 192.168.1.10:6443;
        server 192.168.1.11:6443;
        server 192.168.1.12:6443;
    }

    server {
        listen 6443;
        proxy_pass k3s_servers;
        proxy_timeout 10s;
        proxy_connect_timeout 3s;
    }
}
```

```bash
systemctl restart nginx
```

### keepalived (VIP 구성)

```bash
apt-get install -y keepalived

# MASTER 노드 /etc/keepalived/keepalived.conf
cat > /etc/keepalived/keepalived.conf << 'EOF'
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass k3svip
    }
    virtual_ipaddress {
        192.168.1.100/24
    }
}
EOF

# BACKUP 노드는 state BACKUP, priority 90으로 설정
systemctl enable keepalived
systemctl start keepalived
```

## etcd 스냅샷 및 자동 백업

### 수동 스냅샷 생성

```bash
# 스냅샷 생성
k3s etcd-snapshot save --name mybackup-$(date +%Y%m%d%H%M%S)

# 스냅샷 목록 확인
k3s etcd-snapshot ls

# 기본 스냅샷 경로
ls /var/lib/rancher/k3s/server/db/snapshots/
```

### 자동 스냅샷 설정

```yaml
# /etc/rancher/k3s/config.yaml
etcd-snapshot-schedule-cron: "0 */6 * * *"  # 6시간마다
etcd-snapshot-retention: 10                   # 최근 10개 보관
etcd-snapshot-dir: /backup/k3s-snapshots      # 커스텀 저장 경로
```

또는 설치 시 플래그로 지정:

```bash
curl -sfL https://get.k3s.io | sh -s - server \
  --cluster-init \
  --etcd-snapshot-schedule-cron="0 */6 * * *" \
  --etcd-snapshot-retention=10
```

### S3로 스냅샷 업로드

```bash
# S3 설정
curl -sfL https://get.k3s.io | sh -s - server \
  --cluster-init \
  --etcd-s3 \
  --etcd-s3-bucket=k3s-backups \
  --etcd-s3-region=ap-northeast-2 \
  --etcd-s3-access-key=AKIAIOSFODNN7EXAMPLE \
  --etcd-s3-secret-key=wJalrXUtnFEMI/K7MDENG/bPxRfi

# 또는 config.yaml
etcd-s3: true
etcd-s3-bucket: k3s-backups
etcd-s3-region: ap-northeast-2
etcd-s3-access-key: AKIAIOSFODNN7EXAMPLE
etcd-s3-secret-key: wJalrXUtnFEMI/K7MDENG/bPxRfi
```

## etcd 스냅샷 복원

```bash
# 1. 서버 중지
systemctl stop k3s

# 2. 스냅샷 복원 (첫 번째 서버에서만 실행)
k3s server \
  --cluster-reset \
  --cluster-reset-restore-path=/var/lib/rancher/k3s/server/db/snapshots/mybackup-20240101120000

# 3. 서버 재시작
systemctl start k3s

# 4. 다른 서버 노드에서 (etcd 데이터 삭제 후 재조인)
systemctl stop k3s
rm -rf /var/lib/rancher/k3s/server/db/
systemctl start k3s
```

**주의:** 복원은 클러스터의 모든 현재 데이터를 삭제합니다. 복원 전 현재 상태의 스냅샷을 추가로 생성합니다.

## 노드 관리 및 유지보수

### 서버 노드 순차 업그레이드 (무중단)

```bash
# 1. 첫 번째 서버 업그레이드
systemctl stop k3s
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.30.0+k3s1 sh -
systemctl start k3s

# 노드 정상 확인 후 다음 서버 진행
kubectl get nodes

# 2. 두 번째 서버 반복
# 3. 세 번째 서버 반복
```

### 클러스터 쿼럼 주의사항

etcd 클러스터는 (N/2 + 1) 노드가 정상이어야 동작합니다.

| 서버 수 | 허용 장애 수 |
|---------|-------------|
| 1 | 0 |
| 2 | 0 (권장하지 않음) |
| 3 | 1 |
| 5 | 2 |
| 7 | 3 |

서버 유지보수 시 항상 쿼럼을 유지해야 합니다.
