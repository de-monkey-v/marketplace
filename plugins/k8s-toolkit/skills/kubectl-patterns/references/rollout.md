# 배포/롤아웃 관리

kubectl을 사용한 애플리케이션 배포, 롤아웃 관리, 롤백 패턴을 다룹니다.

## Rolling Update 기본

### RollingUpdate 전략 설정

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 6
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2         # 추가로 생성할 수 있는 파드 수 (정수 또는 %)
      maxUnavailable: 1   # 업데이트 중 사용 불가능할 수 있는 파드 수 (정수 또는 %)
```

### maxSurge와 maxUnavailable 조합 예시

| maxSurge | maxUnavailable | 특성 |
|----------|----------------|------|
| 1 | 0 | 가용성 최우선, 느린 배포 |
| 0 | 1 | 리소스 절약, 순차 교체 |
| 25% | 25% | 기본값, 균형 |
| 100% | 0 | 빠른 배포, 높은 리소스 사용 |

## kubectl rollout 명령어

### 롤아웃 상태 확인

```bash
# 롤아웃 진행 상태 확인
kubectl rollout status deployment/my-app

# --watch 플래그로 완료까지 대기
kubectl rollout status deployment/my-app --watch

# 타임아웃 설정
kubectl rollout status deployment/my-app --timeout=5m

# StatefulSet 롤아웃 상태
kubectl rollout status statefulset/my-statefulset

# DaemonSet 롤아웃 상태
kubectl rollout status daemonset/my-daemonset
```

출력 예시:
```
Waiting for deployment "my-app" rollout to finish: 2 out of 5 new replicas have been updated...
Waiting for deployment "my-app" rollout to finish: 3 out of 5 new replicas have been updated...
Waiting for deployment "my-app" rollout to finish: 4 out of 5 new replicas have been updated...
Waiting for deployment "my-app" rollout to finish: 1 old replicas are pending termination...
deployment "my-app" successfully rolled out
```

### 롤아웃 히스토리

```bash
# 롤아웃 히스토리 조회
kubectl rollout history deployment/my-app

# 특정 리비전 상세 보기
kubectl rollout history deployment/my-app --revision=3

# 변경 사유 기록 (--record는 deprecated, annotation 사용 권장)
kubectl annotate deployment my-app kubernetes.io/change-cause="v2.1.0 배포: 버그 수정 포함"
```

히스토리 출력 예시:
```
REVISION  CHANGE-CAUSE
1         초기 배포 v1.0.0
2         v2.0.0 배포: 새 기능 추가
3         v2.1.0 배포: 버그 수정 포함
```

### 롤백

```bash
# 이전 버전으로 롤백 (직전 리비전)
kubectl rollout undo deployment/my-app

# 특정 리비전으로 롤백
kubectl rollout undo deployment/my-app --to-revision=2

# 롤백 전 히스토리 확인
kubectl rollout history deployment/my-app

# 롤백 상태 확인
kubectl rollout status deployment/my-app
```

### 롤아웃 일시정지/재개

카나리 배포나 단계적 배포 시 유용합니다.

```bash
# 롤아웃 일시정지 (현재 상태에서 멈춤)
kubectl rollout pause deployment/my-app

# 이미지 업데이트 (pause 중에는 실제 롤아웃 안 됨)
kubectl set image deployment/my-app app=myapp:v2

# 여러 변경사항 적용 후 한 번에 재개
kubectl set resources deployment/my-app -c app --limits=cpu=200m,memory=256Mi
kubectl rollout resume deployment/my-app

# 롤아웃 재개 후 상태 확인
kubectl rollout status deployment/my-app
```

## 이미지 업데이트

```bash
# 이미지 업데이트 (기본)
kubectl set image deployment/my-app container-name=new-image:tag

# 예시: nginx 이미지 업데이트
kubectl set image deployment/my-app nginx=nginx:1.25

# 여러 컨테이너 동시 업데이트
kubectl set image deployment/my-app \
  frontend=myapp-frontend:v2 \
  sidecar=my-sidecar:v1.2

# 전체 네임스페이스 모든 파드 이미지 확인
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.image}{" "}{end}{"\n"}{end}'

# 변경 사유 annotation 추가와 함께 업데이트
kubectl set image deployment/my-app app=myapp:v2 && \
  kubectl annotate deployment my-app kubernetes.io/change-cause="v2 배포"
```

## Blue-Green 배포 패턴

두 개의 환경을 유지하고 Service selector를 전환하는 방식입니다.

### 설정

```yaml
# blue-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: app
        image: myapp:v1

---
# green-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: app
        image: myapp:v2

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
    version: blue     # ← 이 부분을 변경하여 전환
  ports:
  - port: 80
    targetPort: 8080
```

### Blue-Green 전환 절차

```bash
# 1. Green 배포 생성
kubectl apply -f green-deployment.yaml

# 2. Green 파드 준비 대기
kubectl rollout status deployment/myapp-green

# 3. Green 파드 동작 확인 (port-forward로 직접 테스트)
kubectl port-forward deployment/myapp-green 8080:8080
# 별도 터미널: curl http://localhost:8080/health

# 4. Service selector를 Green으로 전환
kubectl patch service myapp-service -p '{"spec":{"selector":{"version":"green"}}}'

# 5. 전환 확인
kubectl get endpoints myapp-service

# 6. 정상 동작 확인 후 Blue 제거
kubectl delete deployment myapp-blue
```

## Canary 배포 패턴

트래픽 일부만 새 버전으로 보내는 점진적 배포 방식입니다.

### 기본 Canary 패턴 (레플리카 비율 활용)

```yaml
# stable-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-stable
spec:
  replicas: 9          # 90% 트래픽
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
        track: stable
    spec:
      containers:
      - name: app
        image: myapp:v1

---
# canary-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-canary
spec:
  replicas: 1          # 10% 트래픽
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
        track: canary
    spec:
      containers:
      - name: app
        image: myapp:v2

---
# service.yaml (두 디플로이먼트 모두 선택)
apiVersion: v1
kind: Service
spec:
  selector:
    app: myapp         # track 라벨 없이 둘 다 포함
```

### 점진적 Canary 확대

```bash
# 1. Canary 배포 (1/10 = 10%)
kubectl apply -f canary-deployment.yaml

# 2. 메트릭 모니터링 후 Canary 확대
kubectl scale deployment myapp-canary --replicas=3    # 3/12 = 25%
kubectl scale deployment myapp-stable --replicas=9

# 3. 추가 확대
kubectl scale deployment myapp-canary --replicas=5    # 5/14 = 36%
kubectl scale deployment myapp-stable --replicas=9

# 4. 완전 전환
kubectl set image deployment/myapp-stable app=myapp:v2
kubectl scale deployment myapp-canary --replicas=0    # Canary 제거

# 5. Stable이 v2로 완전 전환되면 Canary 삭제
kubectl delete deployment myapp-canary
```

## 배포 상태 확인 자동화

### 배포 스크립트 패턴

```bash
#!/bin/bash
# deploy-and-verify.sh

DEPLOYMENT="my-app"
NAMESPACE="production"
NEW_IMAGE="myapp:v2"
TIMEOUT=300  # 5분

# 1. 이미지 업데이트
kubectl set image deployment/${DEPLOYMENT} \
  app=${NEW_IMAGE} \
  -n ${NAMESPACE}

# 변경 사유 기록
kubectl annotate deployment ${DEPLOYMENT} \
  kubernetes.io/change-cause="Automated deploy: ${NEW_IMAGE}" \
  -n ${NAMESPACE}

# 2. 롤아웃 완료 대기
if kubectl rollout status deployment/${DEPLOYMENT} \
  -n ${NAMESPACE} \
  --timeout=${TIMEOUT}s; then
  echo "배포 성공: ${NEW_IMAGE}"
  exit 0
else
  echo "배포 실패: 롤백 진행"
  kubectl rollout undo deployment/${DEPLOYMENT} -n ${NAMESPACE}
  exit 1
fi
```

### Deployment Condition 분석

```bash
# 배포 컨디션 확인
kubectl get deployment my-app -o jsonpath='{.status.conditions}' | jq .

# Progressing condition 확인
kubectl get deployment my-app -o jsonpath='{.status.conditions[?(@.type=="Progressing")].message}'

# Available condition 확인
kubectl get deployment my-app -o jsonpath='{.status.conditions[?(@.type=="Available")].status}'
```

## StatefulSet 롤아웃

```bash
# StatefulSet 업데이트 (기본: OnDelete)
# RollingUpdate로 전략 변경 후 적용
kubectl patch statefulset my-statefulset \
  -p '{"spec":{"updateStrategy":{"type":"RollingUpdate"}}}'

# 파티션 기반 단계적 업데이트 (인덱스 3 이상만 업데이트)
kubectl patch statefulset my-statefulset \
  -p '{"spec":{"updateStrategy":{"rollingUpdate":{"partition":3}}}}'

# 롤아웃 상태 확인
kubectl rollout status statefulset/my-statefulset
```

## DaemonSet 롤아웃

```bash
# DaemonSet 이미지 업데이트
kubectl set image daemonset/my-daemonset daemon=my-image:v2

# 롤아웃 상태 확인
kubectl rollout status daemonset/my-daemonset

# 롤백
kubectl rollout undo daemonset/my-daemonset
```
