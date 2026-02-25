# Networking 상세 가이드

Service, Ingress, NetworkPolicy의 상세 패턴과 실전 YAML 예제를 제공합니다.

---

## Service

Service는 Pod 집합에 대한 안정적인 네트워크 엔드포인트를 제공합니다.

### ClusterIP (기본값)

클러스터 내부에서만 접근 가능합니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
  namespace: production
  labels:
    app.kubernetes.io/name: my-app
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: my-app
  ports:
    - name: http
      port: 80          # 서비스 포트
      targetPort: 8080  # 컨테이너 포트
      protocol: TCP
    - name: metrics
      port: 9090
      targetPort: 9090
```

### NodePort

각 노드의 특정 포트로 외부 접근을 허용합니다. (30000-32767 범위)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-nodeport
  namespace: production
spec:
  type: NodePort
  selector:
    app.kubernetes.io/name: my-app
  ports:
    - name: http
      port: 80
      targetPort: 8080
      nodePort: 30080   # 생략 시 자동 할당
```

NodePort는 주로 개발/테스트 환경에서 사용합니다. 프로덕션에서는 LoadBalancer 또는 Ingress를 권장합니다.

### LoadBalancer

클라우드 프로바이더의 외부 로드밸런서를 생성합니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-lb
  namespace: production
  annotations:
    # AWS EKS
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-internal: "true"  # 내부 LB
    # GKE
    # cloud.google.com/load-balancer-type: "Internal"
spec:
  type: LoadBalancer
  selector:
    app.kubernetes.io/name: my-app
  ports:
    - port: 80
      targetPort: 8080
  loadBalancerSourceRanges:
    - "10.0.0.0/8"   # 접근 허용 IP 범위 제한
```

### ExternalName

외부 DNS 이름을 클러스터 내부 이름으로 매핑합니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-db
  namespace: production
spec:
  type: ExternalName
  externalName: db.example.com
```

앱은 `external-db.production.svc.cluster.local`로 접근하면 `db.example.com`으로 리다이렉트됩니다.

### Headless Service

Pod에 직접 DNS 레코드를 부여합니다. StatefulSet과 함께 사용합니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgresql-headless
  namespace: production
spec:
  clusterIP: None   # Headless 핵심
  selector:
    app.kubernetes.io/name: postgresql
  ports:
    - port: 5432
      targetPort: 5432
```

### sessionAffinity (세션 고정)

같은 클라이언트의 요청을 동일 Pod로 전달합니다.

```yaml
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600  # 세션 유지 시간
```

---

## Ingress

클러스터 외부 트래픽을 내부 Service로 라우팅합니다.

### 기본 구조 (NGINX Ingress Controller)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  namespace: production
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.example.com
      secretName: api-example-com-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app
                port:
                  number: 80
```

### Path Types

| pathType | 동작 |
|----------|------|
| `Prefix` | 경로 접두사 매칭 (`/api`는 `/api`, `/api/v1`, `/api/v2` 등 매칭) |
| `Exact` | 정확히 일치하는 경로만 매칭 |
| `ImplementationSpecific` | Ingress 컨트롤러에 따라 다름 |

### 다중 호스트 및 경로 라우팅

```yaml
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.example.com
        - admin.example.com
      secretName: example-com-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /v1
            pathType: Prefix
            backend:
              service:
                name: api-v1
                port:
                  number: 80
          - path: /v2
            pathType: Prefix
            backend:
              service:
                name: api-v2
                port:
                  number: 80
    - host: admin.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: admin-app
                port:
                  number: 80
```

### TLS 설정 (cert-manager 연동)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  namespace: production
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.example.com
      secretName: api-example-com-tls  # cert-manager가 자동 생성
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app
                port:
                  number: 80
```

### Traefik Ingress 어노테이션

```yaml
metadata:
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.middlewares: production-redirect@kubernetescrd
    traefik.ingress.kubernetes.io/router.tls: "true"
    traefik.ingress.kubernetes.io/router.tls.certresolver: letsencrypt
```

### 주요 NGINX 어노테이션

```yaml
metadata:
  annotations:
    # 속도 제한
    nginx.ingress.kubernetes.io/limit-rps: "10"
    nginx.ingress.kubernetes.io/limit-connections: "5"

    # 타임아웃
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "30"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "30"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "30"

    # CORS
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://example.com"

    # 인증
    nginx.ingress.kubernetes.io/auth-url: "https://auth.example.com/verify"
    nginx.ingress.kubernetes.io/auth-signin: "https://auth.example.com/signin"

    # WebSocket
    nginx.ingress.kubernetes.io/proxy-http-version: "1.1"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "Upgrade";
```

---

## NetworkPolicy

Pod 간 네트워크 트래픽을 제어합니다. CNI 플러그인이 NetworkPolicy를 지원해야 합니다 (Calico, Cilium, Weave 등).

### 기본 거부 정책 (Default Deny)

**네임스페이스의 모든 Ingress 트래픽 거부:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}    # 모든 Pod에 적용
  policyTypes:
    - Ingress
```

**모든 트래픽 거부 (Ingress + Egress):**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

### 특정 Pod로부터의 Ingress 허용

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-frontend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: backend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: frontend
      ports:
        - protocol: TCP
          port: 8080
```

### 특정 네임스페이스로부터의 Ingress 허용

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-monitoring
  namespace: production
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: my-app
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: monitoring
          podSelector:
            matchLabels:
              app.kubernetes.io/name: prometheus
      ports:
        - protocol: TCP
          port: 9090
```

`namespaceSelector`와 `podSelector`가 같은 `from` 항목에 있으면 AND 조건입니다. 별도 항목이면 OR 조건입니다.

### Egress 제어

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: backend
  policyTypes:
    - Egress
  egress:
    # DNS 허용 (필수)
    - ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
    # 같은 네임스페이스의 DB Pod 허용
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: postgresql
      ports:
        - protocol: TCP
          port: 5432
    # 외부 API (CIDR 블록)
    - to:
        - ipBlock:
            cidr: 10.0.0.0/8
            except:
              - 10.0.0.0/24   # 특정 대역 제외
      ports:
        - protocol: TCP
          port: 443
```

### Ingress Controller로부터 허용 패턴

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-ingress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: my-app
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ingress-nginx
          podSelector:
            matchLabels:
              app.kubernetes.io/name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8080
```

### 실전 NetworkPolicy 체크리스트

1. **기본 거부 정책을 먼저 적용합니다** - 모든 네임스페이스에 `default-deny-ingress` 설정
2. **DNS 허용을 잊지 않습니다** - Egress 정책 설정 시 UDP/TCP 53 포트 허용 필수
3. **Ingress Controller 접근을 허용합니다** - 외부 트래픽이 들어오는 경로를 반드시 열어야 합니다
4. **모니터링 시스템 접근을 허용합니다** - Prometheus scrape 포트 허용
5. **kube-dns 접근을 허용합니다** - `kube-system` 네임스페이스 DNS Pod에 대한 Egress 허용
