# k3s 스토리지 가이드

## Local Path Provisioner

k3s는 `local-path-provisioner`를 기본 StorageClass로 내장합니다. 동적 PVC 프로비저닝을 지원합니다.

### 기본 동작

```bash
# 기본 StorageClass 확인
kubectl get storageclass
# NAME                   PROVISIONER             RECLAIMPOLICY
# local-path (default)   rancher.io/local-path   Delete

# PVC 생성 예시
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 5Gi
EOF

# PVC 상태 확인
kubectl get pvc my-pvc
```

### 기본 스토리지 경로

Local Path Provisioner는 기본적으로 `/var/lib/rancher/k3s/storage/`에 데이터를 저장합니다.

```bash
# 실제 저장 경로 확인
ls /var/lib/rancher/k3s/storage/
# pvc-abc123_default_my-pvc/
```

### 설정 변경 (config.json)

스토리지 경로와 대기 행동을 변경하려면 ConfigMap을 수정합니다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: local-path-config
  namespace: kube-system
data:
  config.json: |
    {
      "nodePathMap": [
        {
          "node": "DEFAULT_PATH_FOR_NON_LISTED_NODES",
          "paths": ["/data/storage"]
        },
        {
          "node": "node1",
          "paths": ["/ssd/storage", "/hdd/storage"]
        }
      ]
    }
  setup: |
    #!/bin/sh
    set -eu
    mkdir -m 0777 -p "$VOL_DIR"
  teardown: |
    #!/bin/sh
    set -eu
    rm -rf "$VOL_DIR"
```

### Local Path Provisioner 제한사항

- `ReadWriteOnce`만 지원 (단일 노드 마운트)
- 특정 노드에 데이터가 저장되므로 파드를 다른 노드로 이동 시 데이터 접근 불가
- 백업/복제 기능 없음
- 프로덕션 환경에서는 Longhorn, NFS, Ceph 등을 사용합니다

## Longhorn 연동

Longhorn은 Rancher Labs에서 개발한 분산 블록 스토리지 시스템으로, k3s와 잘 통합됩니다.

### 사전 요구사항

```bash
# 모든 노드에 필수 패키지 설치
apt-get install -y open-iscsi util-linux

# iscsid 서비스 활성화
systemctl enable iscsid
systemctl start iscsid

# Longhorn 환경 체크 스크립트 실행
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.6.0/deploy/prerequisite/longhorn-iscsi-installation.yaml
```

### Helm으로 Longhorn 설치

```bash
helm repo add longhorn https://charts.longhorn.io
helm repo update

helm install longhorn longhorn/longhorn \
  --namespace longhorn-system \
  --create-namespace \
  --version 1.6.0 \
  --set defaultSettings.defaultReplicaCount=2 \
  --set defaultSettings.storageMinimalAvailablePercentage=15
```

### kubectl로 Longhorn 설치

```bash
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.6.0/deploy/longhorn.yaml

# 설치 확인
kubectl get pods -n longhorn-system
kubectl get storageclass
```

### Longhorn StorageClass 설정

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn-replicated
provisioner: driver.longhorn.io
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: Immediate
parameters:
  numberOfReplicas: "3"
  staleReplicaTimeout: "2880"
  fromBackup: ""
  fsType: "ext4"
  dataLocality: "disabled"
```

### Longhorn UI 접근

```bash
# NodePort로 접근
kubectl patch svc longhorn-frontend -n longhorn-system -p '{"spec":{"type":"NodePort"}}'
kubectl get svc -n longhorn-system longhorn-frontend

# Port-forward로 임시 접근
kubectl port-forward -n longhorn-system svc/longhorn-frontend 8080:80
```

### Longhorn 백업 설정 (S3)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: longhorn-backup-secret
  namespace: longhorn-system
type: Opaque
stringData:
  AWS_ACCESS_KEY_ID: "AKIAIOSFODNN7EXAMPLE"
  AWS_SECRET_ACCESS_KEY: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  AWS_ENDPOINTS: "https://s3.amazonaws.com"
```

Longhorn UI에서 `Settings > Backup Target`을 `s3://my-bucket@us-east-1/`로 설정하고 위 Secret을 연결합니다.

## NFS Provisioner

### NFS 서버 설정

```bash
# NFS 서버 설치 (Ubuntu)
apt-get install -y nfs-kernel-server

# 공유 디렉토리 생성
mkdir -p /data/nfs/k8s
chown nobody:nogroup /data/nfs/k8s
chmod 0777 /data/nfs/k8s

# /etc/exports 설정
echo "/data/nfs/k8s 192.168.1.0/24(rw,sync,no_subtree_check,no_root_squash)" >> /etc/exports

# NFS 내보내기 적용
exportfs -ra
systemctl restart nfs-kernel-server
```

### 모든 k3s 노드에 NFS 클라이언트 설치

```bash
apt-get install -y nfs-common
```

### nfs-subdir-external-provisioner 설치

```bash
helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
helm repo update

helm install nfs-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
  --namespace nfs-provisioner \
  --create-namespace \
  --set nfs.server=192.168.1.50 \
  --set nfs.path=/data/nfs/k8s \
  --set storageClass.name=nfs-client \
  --set storageClass.defaultClass=false \
  --set storageClass.reclaimPolicy=Retain \
  --set storageClass.archiveOnDelete=false
```

### NFS StorageClass 검증

```bash
# StorageClass 확인
kubectl get storageclass nfs-client

# 테스트 PVC 생성
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nfs-test-pvc
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: nfs-client
  resources:
    requests:
      storage: 1Gi
EOF

kubectl get pvc nfs-test-pvc
```

## StorageClass 관리

### 기본 StorageClass 변경

```bash
# 현재 기본 StorageClass 확인
kubectl get storageclass

# 기존 기본값 제거
kubectl patch storageclass local-path -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'

# 새 기본값 설정
kubectl patch storageclass longhorn -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

### StorageClass 비교

| StorageClass | AccessMode | 복제 | 백업 | 적합한 환경 |
|-------------|------------|------|------|-------------|
| `local-path` | RWO | X | X | 개발, 단일 노드 |
| `longhorn` | RWO | O | O | 소규모 프로덕션 |
| `nfs-client` | RWX | N/A | N/A | 공유 스토리지 |

## 데이터 지속성

### etcd 데이터 경로 (HA 모드)

```
/var/lib/rancher/k3s/server/db/etcd/    # etcd 데이터
/var/lib/rancher/k3s/server/db/snapshots/ # etcd 스냅샷
```

### SQLite 데이터 경로 (단일 노드)

```
/var/lib/rancher/k3s/server/db/state.db  # SQLite 데이터베이스
```

### SQLite vs etcd 선택 기준

| 기준 | SQLite | etcd |
|------|--------|------|
| 사용 환경 | 단일 서버 | HA 멀티 서버 |
| 설정 복잡도 | 간단 | 복잡 |
| 성능 | 낮음 | 높음 |
| HA 지원 | X | O |
| 백업 | 파일 복사 | etcd 스냅샷 |

HA 구성은 최소 3대의 서버 노드가 필요합니다. `references/ha-cluster.md` 참조.
