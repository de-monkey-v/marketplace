# Storage 상세 가이드

PersistentVolume, PersistentVolumeClaim, StorageClass의 상세 패턴과 실전 YAML 예제를 제공합니다.

---

## 개념 정리

Kubernetes 스토리지 추상화 계층:

```
Pod → PVC (요청) → PV (실제 스토리지) → 외부 스토리지 (NFS, EBS, GCE PD 등)
```

- **PersistentVolume (PV)**: 클러스터 관리자가 프로비저닝한 스토리지 리소스
- **PersistentVolumeClaim (PVC)**: 사용자가 스토리지를 요청하는 오브젝트
- **StorageClass**: 동적 프로비저닝을 위한 스토리지 유형 정의

---

## PersistentVolume (PV)

### 접근 모드

| 모드 | 약어 | 설명 |
|------|------|------|
| ReadWriteOnce | RWO | 단일 노드에서 읽기/쓰기 |
| ReadOnlyMany | ROX | 여러 노드에서 읽기만 가능 |
| ReadWriteMany | RWX | 여러 노드에서 읽기/쓰기 |
| ReadWriteOncePod | RWOP | 단일 Pod에서만 읽기/쓰기 (k8s 1.22+) |

### PV 작성 예시

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
  labels:
    type: local
    env: production
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteOnce
  reclaimPolicy: Retain      # 회수 정책
  storageClassName: fast-ssd
  persistentVolumeReclaimPolicy: Retain
  volumeMode: Filesystem     # Filesystem 또는 Block
  # NFS 볼륨 예시
  nfs:
    server: nfs-server.example.com
    path: /exports/data
```

### 회수 정책 (reclaimPolicy)

| 정책 | 동작 |
|------|------|
| `Retain` | PVC 삭제 후에도 PV와 데이터 보존. 관리자가 수동으로 처리해야 함. |
| `Delete` | PVC 삭제 시 PV와 외부 스토리지 모두 자동 삭제 |
| `Recycle` | PV의 데이터를 삭제 후 재사용 (지원 중단, 사용 자제) |

**중요 데이터에는 반드시 `Retain`을 사용합니다.**

---

## PersistentVolumeClaim (PVC)

### PVC 작성 예시

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-app-data
  namespace: production
  labels:
    app.kubernetes.io/name: my-app
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd    # 동적 프로비저닝 사용 시 StorageClass 지정
  resources:
    requests:
      storage: 50Gi
  volumeMode: Filesystem
  # 특정 PV에 바인딩하려면 selector 사용
  # selector:
  #   matchLabels:
  #     type: local
```

### Pod에서 PVC 사용

```yaml
spec:
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: my-app-data
        readOnly: false
  containers:
    - name: app
      volumeMounts:
        - name: data
          mountPath: /var/lib/data
```

### PVC 크기 확장

StorageClass에서 `allowVolumeExpansion: true`가 설정된 경우 PVC 크기를 늘릴 수 있습니다.

```bash
kubectl patch pvc my-app-data -n production \
  -p '{"spec": {"resources": {"requests": {"storage": "100Gi"}}}}'
```

---

## StorageClass

동적 프로비저닝을 통해 PVC 생성 시 자동으로 PV를 프로비저닝합니다.

### AWS EBS 기반 StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
  annotations:
    storageclass.kubernetes.io/is-default-class: "false"
provisioner: ebs.csi.aws.com
parameters:
  type: gp3           # gp2, gp3, io1, io2, st1, sc1
  fsType: ext4
  encrypted: "true"
  kmsKeyId: "arn:aws:kms:..."  # KMS 키 ARN (선택)
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer  # Pod 스케줄링 후 PV 생성
```

### GCE PD 기반 StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
  replication-type: regional-pd   # 리전 복제 (고가용성)
  disk-encryption-kms-key: "projects/.../cryptoKeyVersions/1"
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
```

### volumeBindingMode

| 모드 | 동작 |
|------|------|
| `Immediate` | PVC 생성 즉시 PV 바인딩 (기본값) |
| `WaitForFirstConsumer` | Pod가 스케줄링될 때까지 PV 생성 대기 (권장) |

`WaitForFirstConsumer`를 사용하면 Pod가 스케줄링될 노드와 동일한 가용 영역에 PV가 생성됩니다.

---

## 볼륨 유형

### emptyDir

Pod가 실행되는 동안 임시 저장소를 제공합니다. Pod 삭제 시 데이터도 삭제됩니다.

```yaml
volumes:
  - name: cache
    emptyDir:
      sizeLimit: 1Gi
  - name: tmpfs
    emptyDir:
      medium: Memory  # RAM 기반 (빠르지만 메모리 사용)
      sizeLimit: 512Mi
```

사용 사례: 캐시, 임시 파일, 컨테이너 간 파일 공유.

### hostPath

노드의 파일시스템을 Pod에 마운트합니다.

```yaml
volumes:
  - name: host-data
    hostPath:
      path: /var/log/apps
      type: DirectoryOrCreate  # 없으면 생성
```

| type | 설명 |
|------|------|
| `DirectoryOrCreate` | 없으면 디렉토리 생성 |
| `Directory` | 반드시 존재해야 함 |
| `FileOrCreate` | 없으면 파일 생성 |
| `File` | 반드시 존재해야 함 |
| `Socket` | 유닉스 소켓 |
| `CharDevice` | 문자 디바이스 |
| `BlockDevice` | 블록 디바이스 |

**보안 주의**: hostPath는 노드 파일시스템에 직접 접근하므로 보안 위험이 있습니다. DaemonSet이나 특수 목적 외에는 사용을 피합니다.

### NFS 볼륨

```yaml
volumes:
  - name: nfs-data
    nfs:
      server: nfs-server.example.com
      path: /exports/shared
      readOnly: false
```

### Projected Volumes

여러 볼륨 소스를 하나의 디렉토리로 합칩니다.

```yaml
volumes:
  - name: combined
    projected:
      sources:
        - secret:
            name: my-secret
            items:
              - key: tls.crt
                path: tls/tls.crt
        - configMap:
            name: my-config
            items:
              - key: app.yaml
                path: config/app.yaml
        - serviceAccountToken:
            path: token
            expirationSeconds: 3600
            audience: "my-service"
```

### CSI 볼륨 (Cloud Storage, Secrets Manager 등)

```yaml
volumes:
  - name: aws-secret
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true
      volumeAttributes:
        secretProviderClass: "aws-secrets"
```

---

## StatefulSet의 volumeClaimTemplates

StatefulSet에서 각 Pod마다 독립적인 PVC를 자동 생성합니다.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: kafka
spec:
  replicas: 3
  serviceName: kafka
  template:
    spec:
      containers:
        - name: kafka
          image: confluentinc/cp-kafka:7.5.0
          volumeMounts:
            - name: data
              mountPath: /var/lib/kafka/data
            - name: logs
              mountPath: /var/log/kafka
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast-ssd
        resources:
          requests:
            storage: 100Gi
    - metadata:
        name: logs
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: standard
        resources:
          requests:
            storage: 10Gi
```

생성되는 PVC 이름: `data-kafka-0`, `data-kafka-1`, `data-kafka-2`, `logs-kafka-0` 등.

**주의**: StatefulSet 삭제 시 volumeClaimTemplates로 생성된 PVC는 자동 삭제되지 않습니다. 수동으로 삭제해야 합니다.

---

## 백업 전략

### VolumeSnapshot

```yaml
# VolumeSnapshotClass 생성
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-aws-vsc
driver: ebs.csi.aws.com
deletionPolicy: Delete

---
# VolumeSnapshot 생성
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: my-app-snapshot-20260225
  namespace: production
spec:
  volumeSnapshotClassName: csi-aws-vsc
  source:
    persistentVolumeClaimName: my-app-data

---
# 스냅샷에서 복원
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-app-data-restored
spec:
  dataSource:
    name: my-app-snapshot-20260225
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 50Gi
```

### Velero를 이용한 클러스터 백업

```bash
# 네임스페이스 백업
velero backup create production-backup \
  --include-namespaces production \
  --storage-location default \
  --volume-snapshot-locations default

# 백업에서 복원
velero restore create --from-backup production-backup

# 백업 스케줄 생성
velero schedule create daily-backup \
  --schedule="0 2 * * *" \
  --include-namespaces production
```

---

## 스토리지 선택 가이드

| 사용 사례 | 권장 볼륨 유형 | 접근 모드 |
|-----------|---------------|-----------|
| 데이터베이스 | EBS gp3 / PD SSD | RWO |
| 공유 파일 스토리지 | NFS / EFS / Filestore | RWX |
| 임시 캐시 | emptyDir | - |
| 설정 파일 | ConfigMap / Secret | - |
| 로그 수집 | hostPath | - |
| 고성능 I/O | io1/io2 EBS, pd-extreme | RWO |
