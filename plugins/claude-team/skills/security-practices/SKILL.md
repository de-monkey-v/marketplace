---
name: security-practices
description: "보안 레퍼런스. OWASP Top 10 체크리스트, OAuth2/OIDC/JWT/MFA 인증 플로우, 보안 설계 패턴을 제공합니다."
version: 1.0.0
---

# Security Practices Reference

보안 분석 및 설계를 위한 전문 레퍼런스 스킬입니다. OWASP Top 10 기반 취약점 체크리스트와 최신 인증/인가 패턴을 제공합니다.

## Overview

이 스킬은 다음과 같은 보안 영역을 다룹니다:

- **OWASP Top 10**: 가장 중요한 웹 애플리케이션 보안 위험 체크리스트
- **인증/인가 패턴**: OAuth2, OIDC, JWT, MFA 등 현대적인 인증 메커니즘
- **보안 설계 원칙**: Defense in depth, least privilege, fail secure
- **보안 헤더**: CSP, HSTS, X-Frame-Options 등 필수 HTTP 보안 헤더

## Security Principles

### 1. Defense in Depth (다층 방어)

단일 보안 메커니즘에 의존하지 말고 여러 계층의 보안 통제를 적용합니다.

**예시**:
- 웹 애플리케이션: WAF + Input Validation + Parameterized Queries + Least Privilege DB User
- 인증: Password + MFA + Rate Limiting + Account Lockout

### 2. Least Privilege (최소 권한 원칙)

사용자, 프로세스, 시스템에 필요한 최소한의 권한만 부여합니다.

**적용 예시**:
- 데이터베이스 사용자: SELECT만 필요하면 INSERT/UPDATE/DELETE 권한 제거
- API 토큰: 특정 리소스에 대한 특정 작업만 허용
- 파일 시스템: 애플리케이션은 자신의 디렉토리에만 읽기/쓰기 권한

### 3. Fail Secure (안전한 실패)

오류 발생 시 시스템이 안전한 상태로 전환되도록 설계합니다.

**적용 예시**:
- 인증 실패 시 접근 거부 (접근 허용 아님)
- 권한 확인 중 오류 발생 시 403 Forbidden
- 암호화 실패 시 데이터 전송 중단

### 4. Zero Trust Architecture

네트워크 위치와 관계없이 모든 접근을 검증합니다.

**원칙**:
- 모든 요청에 대해 인증 및 권한 확인
- 네트워크 경계 신뢰하지 않음
- 마이크로 세그멘테이션 적용

## When to Use This Skill

### 보안 검토가 필요한 경우

- 새로운 기능 개발 전 보안 설계 검토
- 코드 리뷰 시 보안 취약점 체크
- 프로덕션 배포 전 보안 체크리스트 확인
- 보안 감사 또는 컴플라이언스 준비

### 인증/인가 구현 시

- 새로운 인증 시스템 설계
- 기존 인증 시스템 마이그레이션
- 서드파티 인증 통합 (OAuth2, OIDC)
- API 보안 강화

### 보안 사고 대응

- 취약점 패치 우선순위 결정
- 보안 사고 원인 분석
- 재발 방지 대책 수립

## Key Concepts

### Authentication vs Authorization

| 개념 | 정의 | 질문 | 메커니즘 |
|------|------|------|----------|
| **Authentication (인증)** | 사용자가 누구인지 확인 | "당신은 누구입니까?" | 패스워드, MFA, 생체인증, 인증서 |
| **Authorization (인가)** | 사용자가 무엇을 할 수 있는지 결정 | "당신은 무엇을 할 수 있습니까?" | RBAC, ABAC, ACL, Policy |

### Encryption

| 타입 | 목적 | 기술 | 사용 시점 |
|------|------|------|-----------|
| **Encryption at Rest** | 저장된 데이터 보호 | AES-256, Transparent Data Encryption | 데이터베이스, 파일 시스템, 백업 |
| **Encryption in Transit** | 전송 중 데이터 보호 | TLS 1.2+, HTTPS | 네트워크 통신, API 호출 |
| **Encryption in Use** | 사용 중 데이터 보호 | Homomorphic Encryption, Secure Enclaves | 고도 보안 요구사항 |

### Hashing vs Encryption

| 특성 | Hashing | Encryption |
|------|---------|------------|
| **역변환** | 불가능 (단방향) | 가능 (양방향) |
| **용도** | 무결성 검증, 패스워드 저장 | 데이터 기밀성 보호 |
| **알고리즘** | SHA-256, bcrypt, argon2 | AES, RSA |
| **출력** | 고정 길이 해시값 | 암호문 (복호화 가능) |

### Symmetric vs Asymmetric Encryption

| 특성 | Symmetric | Asymmetric |
|------|-----------|------------|
| **키** | 동일한 키로 암호화/복호화 | 공개키로 암호화, 개인키로 복호화 |
| **속도** | 빠름 | 느림 |
| **용도** | 대용량 데이터 암호화 | 키 교환, 디지털 서명 |
| **알고리즘** | AES, ChaCha20 | RSA, ECC |

## Reference Files

### 1. owasp-checklist.md

OWASP Top 10 (2021) 기반 종합 보안 체크리스트:

- **A01: Broken Access Control** - 접근 제어 취약점 방지
- **A02: Cryptographic Failures** - 암호화 실패 방지
- **A03: Injection** - SQL/NoSQL/Command Injection 방지
- **A04: Insecure Design** - 안전한 설계 원칙
- **A05: Security Misconfiguration** - 보안 설정 오류 방지
- **A06: Vulnerable Components** - 취약한 컴포넌트 관리
- **A07: Authentication Failures** - 인증 실패 방지
- **A08: Data Integrity Failures** - 데이터 무결성 보호
- **A09: Logging Failures** - 보안 로깅 및 모니터링
- **A10: SSRF** - 서버 측 요청 위조 방지

각 항목마다:
- 상세 설명
- 체크리스트
- 탐지 방법
- 방지 코드 예제

### 2. auth-patterns.md

현대적인 인증/인가 패턴:

- **인증 방법 비교**: Session, JWT, OAuth2, API Key, mTLS
- **JWT 패턴**: 구조, 베스트 프랙티스, 토큰 갱신 플로우
- **OAuth2 플로우**: Authorization Code, PKCE, Client Credentials
- **OIDC**: ID Token, UserInfo, Standard Scopes
- **권한 관리**: RBAC, ABAC
- **MFA**: TOTP, WebAuthn, SMS OTP
- **세션 보안**: 쿠키 설정, 타임아웃
- **패스워드 보안**: 해싱 알고리즘, 정책
- **보안 결정 매트릭스**: 상황별 최적 인증 방법

## Related Agents

이 스킬은 다음 에이전트들과 함께 사용하면 효과적입니다:

### security-architect
보안 아키텍처 설계 및 위협 모델링 전문가. 이 스킬의 체크리스트를 기반으로 시스템 전체 보안 설계를 수행합니다.

### api-designer
API 설계 전문가. auth-patterns.md의 인증/인가 패턴을 활용하여 안전한 API를 설계합니다.

### backend
백엔드 개발 전문가. OWASP 체크리스트를 기반으로 보안 취약점 없는 백엔드 코드를 작성합니다.

### fastapi-expert
FastAPI 전문가. Python/FastAPI 환경에서 보안 패턴을 구현합니다.

### nestjs-expert
NestJS 전문가. TypeScript/NestJS 환경에서 보안 가드, 인터셉터를 구현합니다.

### spring-expert
Spring Boot 전문가. Java/Spring Security를 활용한 엔터프라이즈 보안 구현을 담당합니다.

### devops
인프라 보안, 시크릿 관리, 네트워크 보안, CI/CD 파이프라인 보안을 담당합니다.

## Usage Examples

### 보안 체크리스트 확인

```
사용자: "새로운 사용자 인증 API를 개발했습니다. 보안 체크리스트를 확인해주세요."

에이전트:
1. owasp-checklist.md의 A07 (Authentication Failures) 체크
2. auth-patterns.md에서 적절한 인증 방법 확인
3. 코드 리뷰 및 개선 사항 제안
```

### 인증 시스템 설계

```
사용자: "모바일 앱과 웹 SPA를 위한 인증 시스템을 설계해주세요."

에이전트:
1. auth-patterns.md의 보안 결정 매트릭스 참조
2. OAuth2 + PKCE + JWT 조합 제안
3. 토큰 갱신 플로우 설계
4. 보안 고려사항 체크리스트 제공
```

### 취약점 분석

```
사용자: "SQL Injection 취약점을 찾아주세요."

에이전트:
1. owasp-checklist.md의 A03 (Injection) 참조
2. 코드에서 위험 패턴 검색
3. Parameterized Query 적용 제안
4. 추가 방어 계층 제안 (WAF, Input Validation)
```

## Best Practices

### 보안 검토 프로세스

1. **설계 단계**: 위협 모델링, 보안 요구사항 정의
2. **개발 단계**: OWASP 체크리스트 기반 코드 작성
3. **리뷰 단계**: 보안 체크리스트 확인, 정적 분석
4. **테스트 단계**: 침투 테스트, 취약점 스캔
5. **배포 단계**: 보안 설정 검증, 모니터링 설정

### 우선순위 결정

보안 이슈의 우선순위는 다음 기준으로 결정합니다:

1. **Critical**: 인증 우회, 원격 코드 실행, 민감 데이터 노출
2. **High**: Privilege Escalation, SQL Injection, XSS
3. **Medium**: CSRF, 정보 노출, 약한 암호화
4. **Low**: 설정 개선, 보안 헤더 추가

### 지속적인 보안 개선

- 정기적인 의존성 업데이트
- 자동화된 보안 스캔 (SAST, DAST, SCA)
- 보안 교육 및 인식 제고
- 보안 사고 대응 계획 수립 및 훈련

## Limitations

### 스킬의 한계

- **자동화 한계**: 모든 보안 문제를 자동으로 탐지할 수 없음
- **비즈니스 로직**: 애플리케이션 고유의 비즈니스 로직 보안은 수동 검토 필요
- **제로데이 취약점**: 아직 알려지지 않은 취약점은 다루지 않음

### 보완 방법

- 보안 전문가의 수동 검토
- 침투 테스트
- Bug Bounty 프로그램
- 위협 인텔리전스 구독

## Version History

- **1.0.0** (2026-02-20): 초기 버전
  - OWASP Top 10 (2021) 체크리스트
  - 현대적인 인증/인가 패턴
  - 보안 설계 원칙
