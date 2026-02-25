# 디버깅 워크플로우

kubectl을 사용한 파드 디버깅 절차와 일반적인 오류 해결 방법을 다룹니다.

## 기본 디버깅 단계

파드 문제가 발생하면 다음 순서로 진행합니다.

```
1. kubectl get pod → 현재 상태 확인
2. kubectl describe pod → 이벤트와 원인 확인
3. kubectl logs → 애플리케이션 로그 확인
4. kubectl exec → 컨테이너 내부 직접 확인
5. kubectl debug → ephemeral container로 심화 디버깅
```

## kubectl describe - 이벤트 분석

### 핵심 섹션 분석

```bash
kubectl describe pod my-pod -n my-namespace
```

출력에서 중요하게 확인할 섹션:

```
Name:         my-pod
Namespace:    my-namespace
...
Status:       Pending          ← 현재 상태
...
Conditions:                    ← 파드 컨디션
  Type              Status
  Initialized       True
  Ready             False      ← False면 문제 있음
  ContainersReady   False
  PodScheduled      True
...
Events:                        ← 가장 중요한 섹션
  Type     Reason              Age    From               Message
  ----     ------              ----   ----               -------
  Warning  FailedScheduling    5m     default-scheduler  0/3 nodes are available
  Normal   Scheduled           4m     default-scheduler  Successfully assigned
  Warning  BackOff             2m     kubelet            Back-off pulling image
```

### Conditions 해석

| Condition | False일 때 의미 |
|-----------|----------------|
| PodScheduled | 노드에 스케줄되지 못함 (리소스 부족, 테인트 등) |
| Initialized | Init Container 실패 |
| ContainersReady | 컨테이너 준비되지 않음 |
| Ready | 파드가 트래픽 받을 수 없음 |

### 이벤트 이유(Reason) 코드

| Reason | 의미 |
|--------|------|
| FailedScheduling | 스케줄 실패 |
| Pulling/Pulled | 이미지 풀링 중/완료 |
| Failed | 이미지 풀 실패 |
| BackOff | 재시작 백오프 |
| OOMKilling | 메모리 초과 종료 |
| Evicted | 노드 리소스 부족으로 축출 |

## kubectl logs - 로그 분석

### 기본 로그 명령어

```bash
# 기본 로그 출력
kubectl logs my-pod

# 실시간 로그 스트리밍
kubectl logs my-pod -f

# 마지막 100줄만 출력
kubectl logs my-pod --tail=100

# 최근 1시간 로그
kubectl logs my-pod --since=1h

# 최근 30분 로그
kubectl logs my-pod --since=30m

# 특정 시간 이후 로그 (RFC3339 형식)
kubectl logs my-pod --since-time='2024-01-15T10:00:00Z'

# 이전 컨테이너 로그 (CrashLoopBackOff 시 유용)
kubectl logs my-pod --previous
kubectl logs my-pod -p

# 타임스탬프 포함
kubectl logs my-pod --timestamps
```

### 멀티컨테이너 파드 로그

```bash
# 컨테이너 목록 확인
kubectl get pod my-pod -o jsonpath='{.spec.containers[*].name}'

# 특정 컨테이너 로그
kubectl logs my-pod -c my-container

# 모든 컨테이너 로그 동시 출력
kubectl logs my-pod --all-containers=true

# Init Container 로그
kubectl logs my-pod -c init-container-name
```

### 여러 파드 로그 동시 확인

```bash
# 라벨 셀렉터로 여러 파드 로그 (최근 파드에서만 동작)
kubectl logs -l app=myapp --tail=50

# stern 사용 (설치 필요: https://github.com/stern/stern)
stern myapp                          # 이름 패턴 매칭
stern myapp -n my-namespace          # 네임스페이스 지정
stern myapp --since 1h               # 최근 1시간
stern -l app=myapp                   # 라벨 셀렉터
stern myapp --include "ERROR|WARN"   # 정규식 필터
```

## kubectl exec - 컨테이너 접속

### 기본 접속

```bash
# 대화형 쉘 접속
kubectl exec -it my-pod -- /bin/sh
kubectl exec -it my-pod -- /bin/bash

# 단일 명령 실행
kubectl exec my-pod -- ls /app
kubectl exec my-pod -- cat /etc/config/settings.yaml
kubectl exec my-pod -- env | grep APP_

# 멀티컨테이너 파드에서 특정 컨테이너 접속
kubectl exec -it my-pod -c sidecar -- /bin/sh
```

### exec를 활용한 디버깅

```bash
# 프로세스 확인
kubectl exec my-pod -- ps aux

# 네트워크 연결 확인
kubectl exec my-pod -- netstat -tlnp
kubectl exec my-pod -- ss -tlnp

# DNS 조회 테스트
kubectl exec my-pod -- nslookup my-service
kubectl exec my-pod -- nslookup my-service.my-namespace.svc.cluster.local

# 외부 연결 테스트
kubectl exec my-pod -- curl -v http://my-service:8080/health
kubectl exec my-pod -- wget -O- http://my-service/api/status

# 파일 시스템 확인
kubectl exec my-pod -- df -h
kubectl exec my-pod -- ls -la /var/log/

# 환경변수 확인
kubectl exec my-pod -- printenv
```

## Ephemeral Container (kubectl debug)

기존 파드를 수정하지 않고 임시 디버그 컨테이너를 추가합니다. distroless 이미지처럼 쉘이 없는 컨테이너 디버깅에 유용합니다.

### 기본 사용법

```bash
# 디버그 컨테이너 추가 (busybox 이미지 사용)
kubectl debug -it my-pod --image=busybox --target=my-container

# netshoot으로 네트워크 디버깅
kubectl debug -it my-pod --image=nicolaka/netshoot --target=my-container

# 기존 파드를 복제하여 디버깅 (원본 파드 영향 없음)
kubectl debug my-pod -it --copy-to=debug-pod --image=busybox

# 파드 복제 후 특정 컨테이너 이미지 교체
kubectl debug my-pod -it --copy-to=debug-pod --set-image=myapp=busybox
```

### 노드 디버깅

```bash
# 노드에 특권 컨테이너로 접속
kubectl debug node/my-node -it --image=ubuntu

# 노드 파일시스템은 /host에 마운트됨
# kubectl debug 컨테이너 내에서:
chroot /host
```

## port-forward - 로컬에서 서비스 접근

```bash
# 파드 포트 포워드
kubectl port-forward pod/my-pod 8080:80

# 서비스 포트 포워드
kubectl port-forward svc/my-service 8080:80

# 디플로이먼트 포트 포워드
kubectl port-forward deployment/my-app 8080:8080

# 백그라운드 실행
kubectl port-forward svc/my-service 8080:80 &

# 특정 네임스페이스
kubectl port-forward -n my-namespace svc/my-service 8080:80

# 모든 인터페이스에 바인드 (다른 머신에서 접근 가능)
kubectl port-forward --address 0.0.0.0 svc/my-service 8080:80
```

## 네트워크 디버깅

### DNS 문제 해결

```bash
# DNS 테스트용 파드 실행
kubectl run dns-test --image=busybox --rm -it --restart=Never -- /bin/sh

# 파드 내에서 DNS 확인
nslookup kubernetes.default
nslookup my-service.my-namespace.svc.cluster.local
dig my-service.my-namespace.svc.cluster.local

# CoreDNS 파드 상태 확인
kubectl get pods -n kube-system -l k8s-app=kube-dns

# CoreDNS 로그 확인
kubectl logs -n kube-system -l k8s-app=kube-dns
```

### 연결 테스트

```bash
# 네트워크 테스트용 netshoot 파드 실행
kubectl run netshoot --image=nicolaka/netshoot --rm -it --restart=Never -- /bin/bash

# 파드 내에서:
curl -v http://my-service:80/
tcpdump -i eth0 -n
ping my-service
traceroute my-service
```

### 서비스 엔드포인트 확인

```bash
# 서비스 엔드포인트 확인
kubectl get endpoints my-service

# 엔드포인트가 비어있으면 셀렉터 미스매치 의심
kubectl describe service my-service  # Selector 확인
kubectl get pods -l app=myapp        # 해당 라벨의 파드 확인
```

## CrashLoopBackOff 디버깅

### 원인 분석 체크리스트

```bash
# 1. 현재 상태와 재시작 횟수 확인
kubectl get pod my-pod

# 2. 이전 컨테이너 로그 확인 (핵심)
kubectl logs my-pod --previous

# 3. 이벤트 확인
kubectl describe pod my-pod | grep -A 20 Events

# 4. 컨테이너 종료 상태 확인
kubectl get pod my-pod -o jsonpath='{.status.containerStatuses[0].lastState}'
```

### 일반적인 원인과 해결

| 원인 | 확인 방법 | 해결 |
|------|-----------|------|
| 애플리케이션 크래시 | 로그에서 에러 메시지 확인 | 코드 수정 |
| OOMKilled | `lastState.terminated.reason=OOMKilled` | 메모리 limit 증가 |
| 설정 오류 | 환경변수/ConfigMap 확인 | 설정 수정 |
| Liveness probe 실패 | describe에서 probe 결과 확인 | probe 조정 |
| 의존 서비스 없음 | 로그에서 연결 오류 확인 | 의존성 먼저 배포 |

```bash
# OOMKilled 확인
kubectl get pod my-pod -o jsonpath='{.status.containerStatuses[0].lastState.terminated.reason}'

# Liveness probe 실패 확인
kubectl describe pod my-pod | grep -A 5 "Liveness\|Readiness"

# 종료 코드 확인 (137=OOM, 1=애플리케이션 오류, 143=SIGTERM)
kubectl get pod my-pod -o jsonpath='{.status.containerStatuses[0].lastState.terminated.exitCode}'
```

## ImagePullBackOff 디버깅

```bash
# 1. 이미지 이름/태그 확인
kubectl describe pod my-pod | grep Image:

# 2. 이벤트에서 오류 메시지 확인
kubectl describe pod my-pod | grep -A 5 "Events:"

# 3. imagePullSecrets 확인
kubectl get pod my-pod -o jsonpath='{.spec.imagePullSecrets}'

# 4. 레지스트리 시크릿 확인
kubectl get secret my-registry-secret -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d
```

### 일반적인 원인

```bash
# 원인 1: 이미지가 존재하지 않음
# → 이미지 이름과 태그 확인

# 원인 2: Private registry 접근 권한 없음
# imagePullSecrets 생성
kubectl create secret docker-registry my-registry-secret \
  --docker-server=registry.example.com \
  --docker-username=my-user \
  --docker-password=my-password \
  --docker-email=my-email@example.com

# 파드 스펙에 추가
# spec:
#   imagePullSecrets:
#   - name: my-registry-secret

# 원인 3: 레지스트리 연결 불가
# 노드에서 레지스트리 접근 가능 여부 확인
kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never -- \
  curl -v https://registry.example.com/v2/
```

## Pending 파드 디버깅

```bash
# 스케줄러 이벤트 확인
kubectl describe pod my-pod | grep -A 5 "FailedScheduling"

# 노드 리소스 확인
kubectl describe nodes | grep -A 10 "Allocated resources"

# PVC 바인딩 문제
kubectl get pvc
kubectl describe pvc my-pvc

# 테인트/톨러레이션 확인
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints

# NodeSelector, Affinity 확인
kubectl get pod my-pod -o jsonpath='{.spec.nodeSelector}'
kubectl get pod my-pod -o jsonpath='{.spec.affinity}'
```
