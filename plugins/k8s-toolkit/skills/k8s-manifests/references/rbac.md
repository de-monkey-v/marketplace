# RBAC 상세 가이드

Role, ClusterRole, RoleBinding, ClusterRoleBinding, ServiceAccount 패턴과 Pod Security Standards를 다룹니다.

---

## RBAC 개념 정리

Kubernetes RBAC(Role-Based Access Control)의 핵심 오브젝트:

```
ServiceAccount (주체)
    ↓ (RoleBinding/ClusterRoleBinding으로 연결)
Role/ClusterRole (권한 정의)
    ↓
API 리소스에 대한 동작 허용
```

| 오브젝트 | 범위 | 설명 |
|----------|------|------|
| Role | 네임스페이스 | 특정 네임스페이스 내 리소스 접근 권한 |
| ClusterRole | 클러스터 전체 | 클러스터 전역 리소스 또는 모든 네임스페이스 |
| RoleBinding | 네임스페이스 | 주체에 Role 또는 ClusterRole을 바인딩 |
| ClusterRoleBinding | 클러스터 전체 | 주체에 ClusterRole을 클러스터 전역으로 바인딩 |

---

## Role

특정 네임스페이스 내 리소스에 대한 권한을 정의합니다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
  - apiGroups: [""]         # "" = core API group
    resources: ["pods"]
    verbs: ["get", "watch", "list"]
  - apiGroups: [""]
    resources: ["pods/log"]
    verbs: ["get"]
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch", "update", "patch"]
  # 특정 리소스 이름만 허용
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["my-app-config"]
    verbs: ["get"]
```

### 주요 verbs

| verb | 설명 |
|------|------|
| `get` | 특정 리소스 조회 |
| `list` | 리소스 목록 조회 |
| `watch` | 리소스 변경 감지 |
| `create` | 리소스 생성 |
| `update` | 리소스 전체 업데이트 |
| `patch` | 리소스 부분 업데이트 |
| `delete` | 리소스 삭제 |
| `deletecollection` | 리소스 일괄 삭제 |
| `*` | 모든 동작 허용 |

### 주요 apiGroups

| apiGroups | 리소스 |
|-----------|--------|
| `""` (core) | pods, services, configmaps, secrets, persistentvolumeclaims, serviceaccounts, namespaces 등 |
| `apps` | deployments, statefulsets, daemonsets, replicasets |
| `batch` | jobs, cronjobs |
| `networking.k8s.io` | ingresses, networkpolicies |
| `rbac.authorization.k8s.io` | roles, rolebindings, clusterroles, clusterrolebindings |
| `autoscaling` | horizontalpodautoscalers |
| `storage.k8s.io` | storageclasses, persistentvolumes |

---

## ClusterRole

클러스터 전체 또는 클러스터 범위 리소스에 대한 권한을 정의합니다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
  - apiGroups: [""]
    resources: ["nodes", "nodes/status"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["namespaces"]
    verbs: ["get", "list"]
  - apiGroups: ["metrics.k8s.io"]
    resources: ["nodes", "pods"]
    verbs: ["get", "list"]
```

### ClusterRole Aggregation

여러 ClusterRole을 합쳐서 관리합니다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring
  labels:
    rbac.example.com/aggregate-to-monitoring: "true"
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "endpoints"]
    verbs: ["get", "list", "watch"]

---
# aggregationRule로 자동으로 규칙 합산
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring-admin
aggregationRule:
  clusterRoleSelectors:
    - matchLabels:
        rbac.example.com/aggregate-to-monitoring: "true"
rules: []  # aggregationRule이 자동으로 채움
```

---

## RoleBinding

주체(Subject)에 Role 또는 ClusterRole을 바인딩합니다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-binding
  namespace: production
subjects:
  # ServiceAccount 바인딩
  - kind: ServiceAccount
    name: my-app
    namespace: production
  # 사용자 바인딩
  - kind: User
    name: jane@example.com
    apiGroup: rbac.authorization.k8s.io
  # 그룹 바인딩
  - kind: Group
    name: system:masters
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role        # Role 또는 ClusterRole
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**ClusterRole을 특정 네임스페이스에 바인딩:**
```yaml
# RoleBinding으로 ClusterRole을 사용하면 해당 네임스페이스에만 적용됨
roleRef:
  kind: ClusterRole
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

---

## ClusterRoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: node-reader-binding
subjects:
  - kind: ServiceAccount
    name: metrics-collector
    namespace: monitoring
roleRef:
  kind: ClusterRole
  name: node-reader
  apiGroup: rbac.authorization.k8s.io
```

---

## ServiceAccount

Pod에 ID를 부여하여 API 서버와 통신할 수 있게 합니다.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  namespace: production
  labels:
    app.kubernetes.io/name: my-app
  annotations:
    # AWS IRSA (IAM Role for Service Account)
    eks.amazonaws.com/role-arn: "arn:aws:iam::123456789:role/my-app-role"
automountServiceAccountToken: false   # 자동 마운트 비활성화 (권장)
imagePullSecrets:
  - name: registry-credentials
```

Pod에서 ServiceAccount 사용:
```yaml
spec:
  serviceAccountName: my-app
  automountServiceAccountToken: false  # Pod 레벨에서도 비활성화
```

### 기본 ServiceAccount 주의사항

- 각 네임스페이스에는 `default` ServiceAccount가 자동 생성됩니다.
- `default` ServiceAccount를 앱에 사용하지 않습니다. 전용 ServiceAccount를 만듭니다.
- `automountServiceAccountToken: false`로 불필요한 토큰 마운트를 방지합니다.

---

## 최소 권한 원칙 적용

### 안티패턴 (피해야 할 것)

```yaml
# 나쁜 예: 와일드카드 권한
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]

# 나쁜 예: 불필요한 ClusterRoleBinding
# 특정 네임스페이스만 필요한데 클러스터 전체 권한 부여
```

### 권장 패턴

```yaml
# 좋은 예: 필요한 것만 최소로
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["my-app-config"]  # 특정 리소스만
    verbs: ["get"]                     # 읽기만
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["my-app-secret"]
    verbs: ["get"]
```

### 실전 패턴: Deployment가 필요한 최소 권한

```yaml
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  namespace: production

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: my-app
  namespace: production
rules:
  # 자신의 ConfigMap 읽기
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["my-app-config"]
    verbs: ["get", "watch"]
  # 자신의 Secret 읽기
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["my-app-secret"]
    verbs: ["get"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app
  namespace: production
subjects:
  - kind: ServiceAccount
    name: my-app
    namespace: production
roleRef:
  kind: Role
  name: my-app
  apiGroup: rbac.authorization.k8s.io
```

---

## Pod Security Standards (PSS)

Kubernetes 1.25+에서 PodSecurityPolicy를 대체합니다.

### 세 가지 보안 수준

| 수준 | 설명 | 적합한 환경 |
|------|------|-------------|
| `Privileged` | 제한 없음 | 시스템 수준 워크로드 (e.g., CNI, CSI) |
| `Baseline` | 최소한의 제한 | 일반 앱, 특권이 불필요한 앱 |
| `Restricted` | 최고 수준 제한 | 보안 중요 앱, 모범 사례 준수 |

### PodSecurityAdmission 설정

네임스페이스 레이블로 설정합니다:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted      # 위반 시 거부
    pod-security.kubernetes.io/audit: restricted        # 위반 시 감사 로그
    pod-security.kubernetes.io/warn: restricted         # 위반 시 경고
    pod-security.kubernetes.io/enforce-version: latest
```

모드:
- `enforce`: 정책 위반 시 Pod 생성 거부
- `audit`: 위반 내용을 감사 로그에 기록
- `warn`: 위반 내용을 경고 메시지로 표시

### Restricted 수준을 충족하는 securityContext

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        runAsNonRoot: true
        capabilities:
          drop:
            - ALL
```

### 현재 클러스터 권한 확인

```bash
# 현재 사용자 권한 확인
kubectl auth can-i --list -n production

# 특정 ServiceAccount 권한 확인
kubectl auth can-i list pods \
  --as=system:serviceaccount:production:my-app \
  -n production

# 모든 권한 확인
kubectl auth can-i --list \
  --as=system:serviceaccount:production:my-app \
  -n production
```

---

## 자주 사용하는 ClusterRole 조합

```bash
# 읽기 전용 (기본 제공)
kubectl get clusterrole view

# 편집 권한 (Secrets 제외)
kubectl get clusterrole edit

# 네임스페이스 내 모든 권한
kubectl get clusterrole admin

# 클러스터 전체 관리자
kubectl get clusterrole cluster-admin
```

기본 제공 ClusterRole을 RoleBinding으로 특정 네임스페이스에 바인딩하여 재사용합니다:

```yaml
# 특정 팀에게 production 네임스페이스 view 권한 부여
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: dev-team-view
  namespace: production
subjects:
  - kind: Group
    name: dev-team
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: view
  apiGroup: rbac.authorization.k8s.io
```
