---
name: kubectl-patterns
description: "This skill should be used when the user asks to \"kubectl 사용\", \"리소스 조회\", \"파드 디버깅\", \"로그 확인\", \"kubectl 명령어\", \"클러스터 관리\", \"rollout\", \"scale\", \"kubeconfig\", or mentions kubectl command patterns and cluster operations. Provides kubectl operational patterns and best practices."
version: 0.1.0
---

# kubectl 운영 패턴

kubectl을 사용한 Kubernetes 클러스터 운영 패턴과 모범 사례를 제공합니다.

## Quick Reference - 자주 쓰는 명령어 Top 20

```bash
# 리소스 조회
kubectl get pods                          # 파드 목록
kubectl get pods -n <namespace>           # 네임스페이스 지정
kubectl get pods --all-namespaces         # 전체 네임스페이스
kubectl get pods -o wide                  # 노드 정보 포함
kubectl get all                           # 모든 리소스

# 상세 정보
kubectl describe pod <pod-name>           # 파드 상세 정보
kubectl describe node <node-name>         # 노드 상세 정보

# 로그
kubectl logs <pod-name>                   # 파드 로그
kubectl logs <pod-name> -f                # 실시간 로그
kubectl logs <pod-name> --previous        # 이전 컨테이너 로그
kubectl logs <pod-name> -c <container>    # 특정 컨테이너 로그

# 실행
kubectl exec -it <pod-name> -- /bin/sh    # 파드 내 쉘 접속
kubectl apply -f <file.yaml>              # 매니페스트 적용
kubectl delete -f <file.yaml>             # 매니페스트 삭제

# 스케일/롤아웃
kubectl scale deployment <name> --replicas=3
kubectl rollout status deployment/<name>
kubectl rollout undo deployment/<name>

# 컨텍스트
kubectl config get-contexts               # 컨텍스트 목록
kubectl config use-context <name>         # 컨텍스트 전환

# 포트 포워드
kubectl port-forward pod/<pod-name> 8080:80
kubectl port-forward svc/<svc-name> 8080:80
```

## 안전한 운영 원칙

### 1. 항상 --dry-run=client 먼저 실행

변경 전 영향 범위를 미리 확인합니다.

```bash
# 적용 전 검증
kubectl apply -f deployment.yaml --dry-run=client

# 서버 사이드 검증 (더 정확)
kubectl apply -f deployment.yaml --dry-run=server

# 현재 클러스터 상태와 차이 확인
kubectl diff -f deployment.yaml
```

### 2. 네임스페이스 항상 명시

암묵적인 기본 네임스페이스 사용을 피합니다.

```bash
# 권장: 네임스페이스 명시
kubectl get pods -n production
kubectl apply -f app.yaml -n staging

# 현재 컨텍스트의 기본 네임스페이스 설정
kubectl config set-context --current --namespace=my-namespace
```

### 3. 라벨 셀렉터로 안전하게 선택

```bash
# 먼저 조회로 대상 확인
kubectl get pods -l app=myapp,env=prod

# 확인 후 작업
kubectl delete pods -l app=myapp,env=prod
```

## 출력 형식

```bash
# YAML 형식 (전체 스펙 확인)
kubectl get pod <name> -o yaml

# JSON 형식
kubectl get pod <name> -o json

# 넓은 형식 (추가 컬럼)
kubectl get pods -o wide

# 커스텀 컬럼
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName

# JSONPath로 특정 값 추출
kubectl get pods -o jsonpath='{.items[*].metadata.name}'

# 이름만 출력
kubectl get pods -o name
```

## 위험 명령어 주의사항

다음 명령어는 실행 전 반드시 영향 범위를 확인합니다.

| 명령어 | 위험도 | 주의사항 |
|--------|--------|---------|
| `kubectl delete --all` | 높음 | 네임스페이스의 모든 리소스 삭제 |
| `kubectl drain <node>` | 높음 | 노드의 모든 파드 축출, 서비스 중단 가능 |
| `kubectl cordon <node>` | 중간 | 노드에 새 파드 스케줄링 차단 |
| `kubectl taint node` | 중간 | 기존 파드 퇴거(NoExecute) 가능 |
| `kubectl rollout undo` | 중간 | 이전 버전으로 되돌림 |

```bash
# 삭제 전 대상 확인
kubectl get pods -n mynamespace  # 확인 후
kubectl delete pods --all -n mynamespace  # 실행

# drain 전 파드 확인
kubectl get pods --field-selector spec.nodeName=<node-name>
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
```

## 디버깅 워크플로우 (빠른 참조)

파드 문제 발생 시 순서대로 확인합니다.

```bash
# 1단계: 파드 상태 확인
kubectl get pod <pod-name> -n <namespace>

# 2단계: 이벤트/원인 확인
kubectl describe pod <pod-name> -n <namespace>

# 3단계: 로그 확인
kubectl logs <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --previous  # Crash 시

# 4단계: 직접 접속
kubectl exec -it <pod-name> -n <namespace> -- /bin/sh

# 5단계: 네트워크 디버깅
kubectl port-forward pod/<pod-name> 8080:8080 -n <namespace>
```

## 자주 쓰는 alias

```bash
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgpa='kubectl get pods --all-namespaces'
alias kgs='kubectl get svc'
alias kgd='kubectl get deployment'
alias kdp='kubectl describe pod'
alias kl='kubectl logs'
alias klf='kubectl logs -f'
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
alias kex='kubectl exec -it'
```

## 참고 자료

### Reference Files

- **[`references/resource-management.md`](references/resource-management.md)** - 리소스 CRUD, 라벨/필드 셀렉터, JSONPath, patch, 서버사이드 apply
- **[`references/debugging.md`](references/debugging.md)** - 파드 디버깅 워크플로우, CrashLoopBackOff, ImagePullBackOff, ephemeral container
- **[`references/monitoring.md`](references/monitoring.md)** - kubectl top, 이벤트 분석, 리소스 사용량, 클러스터 상태
- **[`references/rollout.md`](references/rollout.md)** - Rolling Update, rollout 관리, Blue-Green, Canary 패턴
- **[`references/context-config.md`](references/context-config.md)** - kubeconfig 구조, 다중 클러스터 관리, kubectx/kubens
- **[`references/productivity.md`](references/productivity.md)** - alias, 자동완성, kustomize, krew 플러그인, k9s, stern
