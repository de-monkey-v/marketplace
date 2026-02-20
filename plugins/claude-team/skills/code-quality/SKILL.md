---
name: code-quality
description: "코드 품질/리뷰 레퍼런스. 카테고리별 리뷰 체크리스트와 리팩토링 패턴 카탈로그를 제공합니다."
version: 1.0.0
---

# Code Quality Reference

코드 품질 분석 및 리뷰를 위한 전문 레퍼런스 스킬입니다.

## Overview

이 스킬은 코드 리뷰어, 아키텍트, 구현자가 코드 품질을 체계적으로 평가하고 개선하기 위한 레퍼런스를 제공합니다. 주관적 판단에 의존하지 않고, 검증된 원칙과 패턴에 기반한 객관적 기준을 제시합니다.

## When to Use

이 스킬은 다음 상황에서 활용하세요:

- **코드 리뷰**: Pull Request 검토 시 체계적인 체크리스트 적용
- **리팩토링 계획**: 기술 부채 식별 및 개선 방향 수립
- **아키텍처 검증**: 설계 원칙 준수 여부 확인
- **품질 게이트**: 배포 전 품질 기준 통과 검증
- **온보딩**: 신규 팀원에게 팀의 품질 기준 전달
- **기술 부채 분석**: 코드 스멜 식별 및 우선순위 산정

## Key Concepts

### Code Smells

코드에서 더 깊은 문제를 암시하는 표면적 징후:

| Code Smell | 징후 | 심각도 | 주요 리팩토링 |
|-----------|------|--------|--------------|
| Long Method | 메서드가 30줄 이상 | Medium | Extract Method |
| Large Class | 클래스가 300줄 이상 또는 10+ 메서드 | High | Extract Class |
| God Object | 한 클래스가 너무 많은 책임 | Critical | Decompose, Extract |
| Feature Envy | 다른 클래스 데이터를 과도하게 사용 | Medium | Move Method |
| Primitive Obsession | 도메인 개념을 원시 타입으로 표현 | Low | Value Object |
| Long Parameter List | 파라미터 4개 이상 | Medium | Parameter Object |
| Shotgun Surgery | 변경 시 여러 클래스 수정 필요 | High | Move Method/Field |
| Divergent Change | 한 클래스가 여러 이유로 변경 | High | Extract Class |
| Data Clumps | 같은 데이터 그룹이 반복 | Low | Extract Class |
| Switch Statements | 타입 기반 분기 반복 | Medium | Polymorphism |
| Speculative Generality | 미래를 위한 불필요한 추상화 | Low | Inline, Remove |
| Temporary Field | 특정 상황에만 사용되는 필드 | Medium | Extract Class |
| Message Chains | a.b().c().d() 형태 | Medium | Hide Delegate |
| Middle Man | 위임만 하는 클래스 | Low | Remove Middle Man |
| Inappropriate Intimacy | 클래스 간 과도한 결합 | High | Move Method, Extract |
| Duplicate Code | 중복된 로직 | High | Extract Method/Class |
| Dead Code | 사용되지 않는 코드 | Low | Remove |
| Comments | 코드를 설명하는 주석 | Low | Rename, Extract |

### SOLID Principles

객체지향 설계의 5대 원칙:

| Principle | 의미 | 위반 징후 | 준수 방법 |
|-----------|------|-----------|-----------|
| **S**ingle Responsibility | 클래스는 하나의 변경 이유만 | 한 클래스가 여러 이유로 변경 | Extract Class로 책임 분리 |
| **O**pen/Closed | 확장에 열려있고 수정에 닫힘 | 새 기능 추가 시 기존 코드 수정 | 추상화, 전략 패턴 사용 |
| **L**iskov Substitution | 하위 타입은 상위 타입 대체 가능 | 하위 클래스가 상위 계약 위반 | 계약 존중, 적절한 상속 |
| **I**nterface Segregation | 클라이언트별 세분화된 인터페이스 | 사용하지 않는 메서드 구현 강제 | 인터페이스 분리 |
| **D**ependency Inversion | 추상화에 의존, 구체화 의존 금지 | 구체 클래스에 직접 의존 | DI, 인터페이스 사용 |

### Clean Code Principles

읽기 쉽고 유지보수 가능한 코드 작성 원칙:

| Principle | 설명 | 예시 |
|-----------|------|------|
| Meaningful Names | 의도를 드러내는 이름 | `getUserAge()` > `get()` |
| Small Functions | 한 가지 일만 하는 작은 함수 | 함수는 20줄 이내 목표 |
| DRY (Don't Repeat Yourself) | 중복 제거 | 로직 중복 시 함수 추출 |
| YAGNI (You Aren't Gonna Need It) | 필요할 때 구현 | 미래를 위한 추상화 금지 |
| KISS (Keep It Simple, Stupid) | 단순하게 유지 | 과도한 패턴 사용 지양 |
| Boy Scout Rule | 발견한 코드는 개선하고 떠남 | 리팩토링 기회 활용 |
| Fail Fast | 문제 발생 시 즉시 실패 | 입력 검증을 경계에서 |
| Separation of Concerns | 관심사 분리 | UI/비즈니스/데이터 계층 분리 |
| Command-Query Separation | 명령과 조회 분리 | 상태 변경 메서드는 void |
| Tell, Don't Ask | 데이터 요청 말고 행위 요청 | 객체에게 작업 지시 |

### Testing Principles

| Principle | 설명 | 실천 방법 |
|-----------|------|-----------|
| Test Pyramid | Unit > Integration > E2E 비율 | 70% unit, 20% integration, 10% E2E |
| AAA Pattern | Arrange, Act, Assert 구조 | 테스트 코드 구조화 |
| FIRST | Fast, Independent, Repeatable, Self-validating, Timely | 좋은 테스트의 특성 |
| One Assert Per Test | 하나의 테스트는 하나만 검증 | 실패 원인 명확화 |
| Test Behavior, Not Implementation | 구현 세부사항 테스트 금지 | 공개 API만 테스트 |

## References

### review-checklist.md

7개 카테고리로 구성된 종합 코드 리뷰 체크리스트:

1. **Correctness**: 로직 오류, 경계 조건, Null 처리, Race condition 검증
2. **Security**: OWASP Top 10 기준, 입력 검증, 인증/인가, 민감 정보 노출 방지
3. **Performance**: 알고리즘 복잡도, N+1 쿼리, 메모리 누수, 캐싱 기회
4. **Maintainability**: SOLID 원칙, 코드 스멜 탐지, 명명 규칙, 문서화
5. **Architecture Alignment**: 모듈 경계, 의존성 방향, 계층 분리, 순환 의존성
6. **Testing**: 테스트 커버리지, 테스트 품질, Deterministic 검증
7. **Code Style**: 일관성, 죽은 코드, 에러 메시지 품질, 매직 넘버

각 카테고리별로:
- 체크리스트 항목 (체크박스 형식)
- 탐지 패턴 (어떻게 찾을 것인가)
- 심각도 분류 (Critical/Important/Minor/Suggestion)
- 예시 코드 (Before/After)

### refactoring-catalog.md

12가지 핵심 리팩토링 패턴 카탈로그:

각 패턴마다 다음 정보 제공:
- **When to Apply**: 적용 시점 및 코드 스멜
- **Before/After**: 실제 코드 예시 (10-15줄)
- **Safety Steps**: 안전한 리팩토링 절차 (단계별)
- **Risk Level**: Low/Medium/High
- **Prerequisites**: 사전 조건 (예: 테스트 존재)

추가 내용:
- **Safe Refactoring Procedure**: 5단계 안전 절차
- **Anti-Patterns to Avoid**: 피해야 할 리팩토링 실수
- **Decision Matrix**: 코드 스멜 → 리팩토링 패턴 매핑 테이블

## Usage Examples

### Example 1: Pull Request 리뷰

```bash
# PR 리뷰 시 체크리스트 기반 검토
1. review-checklist.md의 7개 카테고리 순회
2. 각 카테고리별 Critical/Important 항목 우선 검토
3. 발견한 이슈를 심각도별로 분류하여 코멘트
4. refactoring-catalog.md에서 적절한 리팩토링 제안
```

### Example 2: 리팩토링 계획

```bash
# 레거시 코드 개선 시
1. Code Smells 테이블로 문제 식별 (Large Class, God Object 등)
2. refactoring-catalog.md에서 Decision Matrix 참조
3. 각 스멜에 대응하는 리팩토링 패턴 선택
4. Risk Level 고려하여 우선순위 결정
5. Safe Refactoring Procedure 따라 점진적 개선
```

### Example 3: 아키텍처 검증

```bash
# 설계 원칙 준수 검증 시
1. SOLID Principles 테이블 기준으로 각 원칙 검토
2. Architecture Alignment 체크리스트 적용
3. 위반 사항 발견 시 refactoring-catalog.md에서 해결책 찾기
4. Extract Interface, Decompose 등 패턴 적용
```

### Example 4: 보안 리뷰

```bash
# 보안 취약점 검토 시
1. review-checklist.md의 Security 섹션 집중 검토
2. OWASP Top 10 퀵 레퍼런스 테이블 확인
3. Input validation, SQL injection, XSS 패턴 탐지
4. 민감 정보 노출 (하드코딩된 시크릿, PII 로깅) 검사
```

## Related Agents

이 스킬은 다음 에이전트들과 함께 사용됩니다:

- **architect**: 아키텍처 설계 시 SOLID 원칙 및 Clean Code 원칙 준수 검증
- **reviewer**: Pull Request 리뷰 시 체크리스트 기반 체계적 검토
- **implementer**: 구현 중 코드 품질 자가 점검 및 리팩토링 적용
- **frontend**: 프론트엔드 코드 리뷰 시 성능 체크리스트 (re-render, bundle size)
- **backend**: 백엔드 코드 리뷰 시 보안, N+1 쿼리, 알고리즘 복잡도 검토
- **tester**: 테스트 코드 품질 검증 (FIRST 원칙, Test Pyramid)
- **security**: 보안 리뷰 시 OWASP 체크리스트 및 보안 패턴 적용
- **performance**: 성능 최적화 시 Performance 체크리스트 및 리팩토링 적용

## Best Practices

### 리뷰 시

1. **체계적 접근**: 카테고리별로 순차 검토 (감정/직관 배제)
2. **심각도 분류**: Critical → Important → Minor → Suggestion 순으로 우선순위
3. **건설적 피드백**: 문제 지적과 함께 refactoring-catalog.md에서 해결책 제안
4. **일관성 유지**: 동일 기준을 모든 코드에 공평하게 적용

### 리팩토링 시

1. **테스트 먼저**: 리팩토링 전 테스트가 반드시 존재하고 통과해야 함
2. **점진적 개선**: 한 번에 하나의 리팩토링만 (Big Bang 금지)
3. **안전 절차**: Safe Refactoring Procedure 5단계 준수
4. **커밋 단위**: 각 리팩토링 후 즉시 커밋 (롤백 가능하도록)

### 품질 기준 수립 시

1. **팀 컨센서스**: 체크리스트를 팀 상황에 맞게 커스터마이징
2. **자동화**: 가능한 항목은 린터/정적 분석 도구로 자동화
3. **측정**: 코드 스멜 빈도, 리팩토링 전후 메트릭 수집
4. **지속 개선**: 리뷰 결과를 바탕으로 체크리스트 개선

## Tips

- **False Positive 주의**: 모든 규칙에는 예외가 있음. 맥락 고려 필수
- **Over-engineering 경계**: YAGNI 원칙 - 현재 필요한 만큼만 리팩토링
- **Premature Abstraction 방지**: Rule of Three - 중복이 3번 나타날 때 추상화
- **레거시 코드**: Characterization Test 먼저 작성 후 리팩토링 시작
- **리뷰 시간 관리**: Critical/Important 이슈에 집중, Minor는 자동화 도구 활용

## Limitations

- 이 레퍼런스는 일반적 원칙과 패턴을 제공하며, 모든 상황에 기계적으로 적용할 수 없음
- 언어별, 프레임워크별 특수한 관행은 별도 참조 필요
- 도메인 특수성 (예: 금융, 의료)은 추가 규칙 필요
- 성능과 가독성 사이 트레이드오프는 맥락에 따라 판단 필요

## Version History

- **1.0.0** (2026-02-20): 초기 버전
  - 7개 카테고리 리뷰 체크리스트
  - 12개 핵심 리팩토링 패턴
  - SOLID, Clean Code, Testing 원칙 레퍼런스
