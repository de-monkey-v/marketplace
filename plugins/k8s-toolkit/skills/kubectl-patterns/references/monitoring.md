# 모니터링 패턴

kubectl을 사용한 클러스터 및 워크로드 모니터링 패턴을 다룹니다.

## kubectl top - 리소스 사용량

Metrics Server가 설치되어 있어야 합니다.

```bash
# Metrics Server 설치 확인
kubectl get deployment metrics-server -n kube-system
```

### 파드 리소스 사용량

```bash
# 기본 파드 리소스 사용량
kubectl top pods

# 특정 네임스페이스
kubectl top pods -n production

# 전체 네임스페이스
kubectl top pods -A
kubectl top pods --all-namespaces

# 컨테이너별 분리 출력
kubectl top pods --containers

# CPU 기준 정렬
kubectl top pods --sort-by=cpu

# 메모리 기준 정렬
kubectl top pods --sort-by=memory

# 라벨 셀렉터 사용
kubectl top pods -l app=myapp
```

출력 예시:
```
NAME                     CPU(cores)   MEMORY(bytes)
myapp-7d9c5f8b4-abc12    125m         256Mi
myapp-7d9c5f8b4-def34    98m          231Mi
nginx-84c9b5d5d-xyz89    5m           15Mi
```

### 노드 리소스 사용량

```bash
# 노드 리소스 사용량
kubectl top nodes

# CPU 기준 정렬
kubectl top nodes --sort-by=cpu

# 메모리 기준 정렬
kubectl top nodes --sort-by=memory
```

출력 예시:
```
NAME           CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
node-1         1250m        31%    4856Mi           63%
node-2         890m         22%    3612Mi           47%
```

## kubectl describe node - 상세 리소스 분석

```bash
kubectl describe node my-node
```

### 핵심 섹션 분석

```
Capacity:                          ← 노드 총 리소스
  cpu:                8
  memory:             16384Mi
  pods:               110

Allocatable:                       ← 파드에 할당 가능한 리소스 (시스템 예약 제외)
  cpu:                7800m
  memory:             15360Mi
  pods:               110

Allocated resources:               ← 현재 할당된 리소스
  (Total limits may be over 100 percent, i.e., overcommitted)
  Resource           Requests     Limits
  --------           --------     ------
  cpu                4200m (53%)  8000m (102%)
  memory             6144Mi (40%) 12288Mi (80%)
```

### 노드 상태 확인

```bash
# 모든 노드 상태 확인
kubectl get nodes
kubectl get nodes -o wide

# 노드 컨디션 확인
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .status.conditions[*]}{.type}={.status}{" "}{end}{"\n"}{end}'

# NotReady 노드 찾기
kubectl get nodes --field-selector='status.conditions[?(@.type=="Ready")].status!=True'

# 노드 테인트 확인
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints
```

## kubectl get events - 이벤트 분석

### 기본 이벤트 조회

```bash
# 현재 네임스페이스 이벤트
kubectl get events

# 전체 네임스페이스 이벤트
kubectl get events -A

# 특정 네임스페이스 이벤트
kubectl get events -n production

# 시간 순 정렬 (최신 이벤트 마지막)
kubectl get events --sort-by='.lastTimestamp'

# Warning 이벤트만 필터
kubectl get events --field-selector type=Warning

# 특정 오브젝트 관련 이벤트
kubectl get events --field-selector involvedObject.name=my-pod

# 특정 종류의 이벤트
kubectl get events --field-selector reason=BackOff
```

### 이벤트 상세 출력

```bash
# 커스텀 컬럼으로 상세 출력
kubectl get events -o custom-columns=\
TIME:.lastTimestamp,\
TYPE:.type,\
REASON:.reason,\
OBJECT:.involvedObject.name,\
MESSAGE:.message

# watch 모드로 실시간 이벤트 모니터링
kubectl get events -w

# 이벤트 타입별 카운트 (파이프 활용)
kubectl get events --field-selector type=Warning | awk '{print $5}' | sort | uniq -c | sort -rn
```

### 주요 경고 이벤트 패턴

| 이벤트 | 의미 | 대응 |
|--------|------|------|
| `OOMKilling` | 메모리 부족으로 컨테이너 종료 | 메모리 limit 증가 |
| `BackOff` | 이미지 풀 또는 재시작 백오프 | 로그 확인, 설정 점검 |
| `FailedScheduling` | 파드 스케줄 실패 | 노드 리소스/테인트 확인 |
| `Evicted` | 노드 압력으로 파드 축출 | 리소스 requests 설정 |
| `FailedMount` | 볼륨 마운트 실패 | PVC/PV 상태 확인 |
| `NetworkNotReady` | 네트워크 플러그인 문제 | CNI 상태 확인 |

## 리소스 사용량 분석

### Requests vs Limits vs Actual 비교

```bash
# 파드별 requests/limits 확인
kubectl get pods -o json | jq -r '.items[] |
  .metadata.name + "\t" +
  (.spec.containers[0].resources.requests.cpu // "none") + "\t" +
  (.spec.containers[0].resources.limits.cpu // "none")'

# 리소스 없는 파드 찾기 (requests/limits 미설정)
kubectl get pods -o json | jq -r '.items[] |
  select(.spec.containers[0].resources.requests == null) |
  .metadata.name'
```

### QoS 클래스 확인

```bash
# 파드 QoS 클래스 확인
kubectl get pod my-pod -o jsonpath='{.status.qosClass}'

# 전체 파드 QoS 클래스 목록
kubectl get pods -o custom-columns=NAME:.metadata.name,QOS:.status.qosClass

# Guaranteed QoS: requests == limits (가장 높은 우선순위)
# Burstable QoS: requests < limits
# BestEffort QoS: requests/limits 없음 (가장 낮은 우선순위, Eviction 우선 대상)
```

### LimitRange 확인

```bash
# 네임스페이스 LimitRange 확인
kubectl get limitrange
kubectl describe limitrange

# ResourceQuota 확인
kubectl get resourcequota
kubectl describe resourcequota
```

## 클러스터 상태 모니터링

### 클러스터 정보

```bash
# 클러스터 기본 정보
kubectl cluster-info

# 컴포넌트 상태 (deprecated in newer versions)
kubectl get componentstatuses

# API 서버 상태
kubectl get --raw /healthz
kubectl get --raw /readyz
kubectl get --raw /livez

# API 서버 메트릭
kubectl get --raw /metrics | grep apiserver_request_total
```

### 컨트롤 플레인 컴포넌트

```bash
# kube-system 파드 상태
kubectl get pods -n kube-system

# etcd 상태
kubectl get pods -n kube-system -l component=etcd

# API 서버 로그
kubectl logs -n kube-system kube-apiserver-<node-name>

# 컨트롤러 매니저 로그
kubectl logs -n kube-system kube-controller-manager-<node-name>

# 스케줄러 로그
kubectl logs -n kube-system kube-scheduler-<node-name>
```

### 워커 노드 모니터링

```bash
# 노드 상태 개요
kubectl get nodes -o wide

# 노드별 파드 수 확인
kubectl get pods -A -o wide | awk '{print $8}' | sort | uniq -c | sort -rn

# 특정 노드의 파드 목록
kubectl get pods -A --field-selector spec.nodeName=my-node

# 노드 capacity 대비 사용률
kubectl describe nodes | grep -A 5 "Allocated resources"
```

## 지속적인 모니터링

### watch 모드

```bash
# 파드 상태 실시간 감시
kubectl get pods -w
kubectl get pods --watch

# 이벤트 실시간 감시
kubectl get events -w --sort-by='.lastTimestamp'

# 파드 상태 변화 감시 (특정 네임스페이스)
kubectl get pods -n production -w

# watch + grep 조합 (별도 터미널)
watch -n 2 'kubectl get pods -n production'
```

### 유용한 모니터링 원라이너

```bash
# 모든 네임스페이스의 Pending/Error 파드 찾기
kubectl get pods -A | grep -v Running | grep -v Completed

# 재시작 횟수가 많은 파드 찾기
kubectl get pods -A --sort-by='.status.containerStatuses[0].restartCount' | tail -20

# 오래된 파드 찾기 (생성 시간 기준 정렬)
kubectl get pods -A --sort-by='.metadata.creationTimestamp'

# 각 네임스페이스의 파드 수 집계
kubectl get pods -A --no-headers | awk '{print $1}' | sort | uniq -c | sort -rn

# 노드별 리소스 사용 현황
kubectl top nodes && echo "---" && kubectl describe nodes | grep -E "Name:|Allocated"
```

## HPA/VPA 모니터링

```bash
# HPA 상태 확인
kubectl get hpa
kubectl describe hpa my-hpa

# HPA 상세 (현재 메트릭 포함)
kubectl get hpa my-hpa -o yaml

# HPA 이벤트 확인
kubectl describe hpa my-hpa | grep -A 10 Events
```
