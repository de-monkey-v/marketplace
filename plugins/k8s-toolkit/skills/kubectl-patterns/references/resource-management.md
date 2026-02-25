# 리소스 관리 패턴

kubectl을 사용한 Kubernetes 리소스 생성, 조회, 수정, 삭제 패턴을 다룹니다.

## CRUD 기본 패턴

### Create (생성)

```bash
# 파일로 생성
kubectl create -f resource.yaml

# 명령형으로 생성
kubectl create deployment nginx --image=nginx:1.25
kubectl create service clusterip my-svc --tcp=80:8080
kubectl create configmap my-config --from-file=config.properties
kubectl create secret generic my-secret --from-literal=password=1234
kubectl create namespace my-namespace

# 생성 후 YAML 확인 (--dry-run 활용)
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml > deployment.yaml
```

### Apply (선언적 적용)

```bash
# 파일 적용
kubectl apply -f deployment.yaml

# 디렉토리 내 모든 파일 적용
kubectl apply -f ./manifests/

# URL에서 직접 적용
kubectl apply -f https://raw.githubusercontent.com/example/repo/main/deploy.yaml

# 재귀적으로 적용
kubectl apply -f ./manifests/ -R

# 서버 사이드 apply (충돌 해결에 유리)
kubectl apply -f deployment.yaml --server-side
```

### apply vs create 차이

| 구분 | `kubectl create` | `kubectl apply` |
|------|-----------------|-----------------|
| 방식 | 명령적(Imperative) | 선언적(Declarative) |
| 이미 존재할 때 | 오류 발생 | 변경 사항만 적용 |
| 관리 방식 | 단일 명령으로 관리 | 파일 기반으로 관리 |
| CI/CD 적합성 | 낮음 | 높음 |
| 권장 상황 | 임시 테스트 | 프로덕션 운영 |

### Get (조회)

```bash
# 기본 조회
kubectl get pods
kubectl get deployments
kubectl get services
kubectl get configmaps
kubectl get secrets

# 여러 리소스 동시 조회
kubectl get pods,services,deployments

# 특정 리소스 조회
kubectl get pod my-pod
kubectl get deployment my-app

# 전체 네임스페이스 조회
kubectl get pods -A
kubectl get pods --all-namespaces
```

### Describe (상세 조회)

```bash
# 파드 상세 정보 (이벤트, 마운트, 컨테이너 상태)
kubectl describe pod my-pod

# 노드 상세 정보 (리소스, 테인트, 컨디션)
kubectl describe node my-node

# 서비스 상세 정보 (엔드포인트 포함)
kubectl describe service my-service

# 디플로이먼트 상세
kubectl describe deployment my-deployment
```

### Delete (삭제)

```bash
# 파일로 삭제
kubectl delete -f resource.yaml

# 이름으로 삭제
kubectl delete pod my-pod
kubectl delete deployment my-deployment

# 라벨로 삭제
kubectl delete pods -l app=myapp

# 강제 삭제 (Terminating 상태 해제)
kubectl delete pod my-pod --force --grace-period=0

# 네임스페이스 내 모든 파드 삭제 (주의!)
kubectl delete pods --all -n my-namespace
```

## 라벨 셀렉터

### 기본 셀렉터

```bash
# 단일 라벨 매칭
kubectl get pods -l app=myapp

# 여러 라벨 AND 조건
kubectl get pods -l app=myapp,env=production

# 라벨 NOT 조건
kubectl get pods -l env!=production

# 라벨 존재 여부
kubectl get pods -l 'app'           # app 라벨이 있는 파드
kubectl get pods -l '!app'          # app 라벨이 없는 파드
```

### Set 기반 셀렉터

```bash
# 값이 여러 개 중 하나인 경우 (IN)
kubectl get pods -l 'env in (production, staging)'

# 값이 여러 개 중 하나도 아닌 경우 (NOTIN)
kubectl get pods -l 'env notin (development, testing)'

# 복합 조건
kubectl get pods -l 'app in (frontend,backend),env=production'
```

### 라벨 관리

```bash
# 라벨 추가
kubectl label pod my-pod tier=frontend

# 라벨 수정 (--overwrite 필요)
kubectl label pod my-pod tier=backend --overwrite

# 라벨 삭제 (키 뒤에 - 추가)
kubectl label pod my-pod tier-

# 모든 파드에 라벨 추가
kubectl label pods --all environment=testing
```

## 필드 셀렉터

```bash
# 실행 중인 파드만 조회
kubectl get pods --field-selector status.phase=Running

# 특정 이름의 리소스 조회
kubectl get pods --field-selector metadata.name=my-pod

# 특정 노드의 파드 조회
kubectl get pods --field-selector spec.nodeName=my-node

# 복합 필드 셀렉터
kubectl get pods --field-selector status.phase=Running,spec.nodeName=my-node

# 실패한 파드 조회
kubectl get pods --field-selector status.phase=Failed

# 전체 네임스페이스에서 필드 셀렉터 사용
kubectl get pods --all-namespaces --field-selector status.phase=Pending
```

## JSONPath 출력

### 기본 JSONPath

```bash
# 파드 이름 목록
kubectl get pods -o jsonpath='{.items[*].metadata.name}'

# 파드의 IP 주소
kubectl get pods -o jsonpath='{.items[*].status.podIP}'

# 특정 파드의 이미지
kubectl get pod my-pod -o jsonpath='{.spec.containers[0].image}'

# 모든 컨테이너 이미지 (모든 파드)
kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}'
```

### 고급 JSONPath

```bash
# range로 각 항목 반복 출력
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\n"}{end}'

# 조건부 필터 (filter expression)
kubectl get pods -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}'

# 중첩된 값 추출
kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type=="ExternalIP")].address}'

# 특정 시크릿 값 디코딩
kubectl get secret my-secret -o jsonpath='{.data.password}' | base64 --decode
```

### 정렬 및 필터링

```bash
# 생성 시간 기준 정렬
kubectl get pods --sort-by='.metadata.creationTimestamp'

# 이름 기준 정렬
kubectl get pods --sort-by='.metadata.name'

# 재시작 횟수 기준 정렬 (많은 순)
kubectl get pods --sort-by='.status.containerStatuses[0].restartCount'
```

## Custom Columns

```bash
# 기본 커스텀 컬럼
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase

# 노드 정보 포함
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName,IP:.status.podIP

# 이미지 정보
kubectl get pods -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image

# 재시작 횟수 포함
kubectl get pods -o custom-columns=NAME:.metadata.name,RESTARTS:.status.containerStatuses[0].restartCount,AGE:.metadata.creationTimestamp

# 파일로 컬럼 정의
# columns.txt:
# NAME          READY         STATUS        RESTARTS
# .metadata.name .status.containerStatuses[0].ready .status.phase .status.containerStatuses[0].restartCount
kubectl get pods -o custom-columns-file=columns.txt
```

## Patch 명령어

### Strategic Merge Patch (기본값)

쿠버네티스 리소스 구조를 이해하고 스마트하게 병합합니다.

```bash
# 레플리카 수 변경
kubectl patch deployment my-app -p '{"spec":{"replicas":3}}'

# 이미지 업데이트
kubectl patch deployment my-app -p '{"spec":{"template":{"spec":{"containers":[{"name":"app","image":"myapp:v2"}]}}}}'

# 리소스 제한 추가
kubectl patch deployment my-app -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "app",
          "resources": {
            "limits": {"cpu": "500m", "memory": "256Mi"},
            "requests": {"cpu": "250m", "memory": "128Mi"}
          }
        }]
      }
    }
  }
}'
```

### JSON Merge Patch

```bash
kubectl patch deployment my-app --type=merge -p '{"spec":{"replicas":5}}'
```

### JSON Patch (RFC 6902)

배열의 특정 인덱스를 정밀하게 수정할 때 사용합니다.

```bash
# 특정 인덱스의 컨테이너 이미지 변경
kubectl patch pod my-pod --type=json \
  -p='[{"op": "replace", "path": "/spec/containers/0/image", "value": "nginx:1.25"}]'

# 환경변수 추가
kubectl patch deployment my-app --type=json \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/env/-", "value": {"name": "DEBUG", "value": "true"}}]'

# 필드 제거
kubectl patch deployment my-app --type=json \
  -p='[{"op": "remove", "path": "/spec/template/spec/containers/0/resources/limits"}]'
```

## 벌크 작업

```bash
# 라벨로 여러 파드 삭제
kubectl delete pods -l app=myapp -n production

# 모든 네임스페이스의 실패 파드 삭제
kubectl delete pods --all-namespaces --field-selector status.phase=Failed

# 전체 네임스페이스 파드 재시작
kubectl rollout restart deployment --all -n my-namespace

# xargs와 조합한 벌크 작업
kubectl get pods -o name | xargs kubectl delete

# 조건에 맞는 파드만 삭제
kubectl get pods --field-selector status.phase=Evicted -o name | xargs kubectl delete

# 여러 파일 한 번에 적용
kubectl apply -f manifest1.yaml -f manifest2.yaml -f manifest3.yaml

# 디렉토리의 모든 YAML 적용
for f in ./manifests/*.yaml; do kubectl apply -f "$f"; done
```

## 서버 사이드 Apply

`--server-side` 플래그를 사용하면 서버가 필드 소유권을 추적합니다.

```bash
# 서버 사이드 apply
kubectl apply -f deployment.yaml --server-side

# 관리자로 강제 적용 (필드 소유권 충돌 해결)
kubectl apply -f deployment.yaml --server-side --force-conflicts

# 필드 관리자 지정
kubectl apply -f deployment.yaml --server-side --field-manager=my-controller
```

### apply vs 서버사이드 apply 비교

| 구분 | 클라이언트 사이드 apply | 서버 사이드 apply |
|------|----------------------|-----------------|
| 필드 소유권 | 없음 | 추적됨 |
| 충돌 감지 | 불완전 | 정확 |
| 대용량 오브젝트 | 제한 (annotation 크기) | 제한 없음 |
| GitOps 적합성 | 보통 | 높음 |

## 리소스 편집

```bash
# 기본 편집기로 리소스 편집
kubectl edit deployment my-app

# 특정 편집기 사용
KUBE_EDITOR=nano kubectl edit deployment my-app
KUBE_EDITOR="code --wait" kubectl edit deployment my-app

# 편집 후 자동 재적용됨
```
