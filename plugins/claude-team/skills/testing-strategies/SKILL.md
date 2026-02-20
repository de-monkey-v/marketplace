---
name: testing-strategies
description: "테스트 전략/패턴 레퍼런스. 유닛/통합/E2E 테스트 패턴, 프레임워크별 가이드, 커버리지 분석 가이드를 제공합니다."
version: 1.0.0
---

# Testing Strategies Reference

테스트 전략 수립 및 테스트 코드 작성을 위한 전문 레퍼런스 스킬입니다.

## Overview

효과적인 테스트 전략은 품질 보증과 리팩토링 신뢰성의 기반입니다. 이 스킬은 다음을 제공합니다:

- **테스트 피라미드 원칙**: 유닛/통합/E2E 테스트의 적절한 비율과 배치 전략
- **패턴 카탈로그**: 프레임워크별 테스트 패턴과 안티패턴
- **커버리지 분석**: 측정 기법과 테스트 케이스 설계 기법
- **프레임워크 가이드**: Jest, Vitest, JUnit, pytest, Go testing 등 주요 프레임워크별 실전 예제

## Test Pyramid Concept

```
        /\
       /  \        E2E Tests
      /    \       - Few (5-10%)
     /------\      - Slow execution
    /        \     - High cost
   /          \    - Full system verification
  /------------\
 /              \  Integration Tests
/                \ - Some (20-30%)
|----------------|  - Medium speed
|                |  - Moderate cost
|                |  - Component interaction
|----------------|
|                |
|   Unit Tests   |  - Many (60-75%)
|                |  - Fast execution
|                |  - Low cost
|________________|  - Business logic focus
```

### Pyramid Principles

1. **Base Layer (Unit Tests)**: 가장 많은 수, 가장 빠른 실행
   - 비즈니스 로직, 알고리즘, 계산, 변환 로직
   - 외부 의존성 완전 격리 (mocks/stubs)
   - 밀리초 단위 실행 시간

2. **Middle Layer (Integration Tests)**: 적당한 수, 적당한 속도
   - 서비스 간 상호작용, DB 연동, API 엔드포인트
   - 실제 인프라 사용 (테스트 DB, 메시지 큐 등)
   - 초 단위 실행 시간

3. **Top Layer (E2E Tests)**: 소수만 유지, 느린 실행
   - 핵심 사용자 시나리오, 크리티컬 패스
   - 전체 시스템 통합 (UI + API + DB + 외부 서비스)
   - 분 단위 실행 시간

## When to Use This Skill

### Primary Use Cases

1. **신규 프로젝트 테스트 전략 수립**
   - 적절한 테스트 도구 선택
   - 커버리지 목표 설정
   - CI/CD 파이프라인 통합

2. **테스트 코드 작성 및 리팩토링**
   - 패턴 참조로 일관성 있는 테스트 작성
   - 안티패턴 식별 및 개선
   - Flaky test 해결

3. **커버리지 분석 및 개선**
   - 미흡한 테스트 영역 식별
   - 우선순위 기반 테스트 케이스 추가
   - 효율적인 테스트 케이스 설계

4. **코드 리뷰 및 품질 검증**
   - 테스트 품질 평가 기준 적용
   - 테스트 가독성 및 유지보수성 개선
   - 테스트 실행 시간 최적화

### When NOT to Use

- 단순한 getter/setter 테스트 작성
- 프레임워크 자체 동작 검증 (이미 검증됨)
- 100% 커버리지 강요 (비효율적)

## Key Concepts

### Test Types Comparison

| Test Type | Scope | Dependencies | Speed | Cost | Purpose |
|-----------|-------|--------------|-------|------|---------|
| **Unit** | 단일 함수/클래스 | 모두 mocking | 매우 빠름 (ms) | 낮음 | 로직 정확성 검증 |
| **Integration** | 여러 컴포넌트 | 일부 실제 사용 | 보통 (초) | 중간 | 상호작용 검증 |
| **E2E** | 전체 시스템 | 모두 실제 사용 | 느림 (분) | 높음 | 사용자 시나리오 검증 |
| **Contract** | API 경계 | API 스펙 | 빠름 (ms) | 낮음 | 서비스 간 계약 검증 |

### Testing Principles

#### FIRST Principles

- **F**ast: 테스트는 빠르게 실행되어야 함 (개발자가 자주 실행할 수 있도록)
- **I**ndependent: 테스트 간 의존성 없음 (순서 무관하게 실행 가능)
- **R**epeatable: 언제 어디서나 동일한 결과 (환경에 독립적)
- **S**elf-validating: 명확한 pass/fail (수동 확인 불필요)
- **T**imely: 코드 작성과 동시에 테스트 작성 (TDD 또는 최소한 동시 작성)

#### Test Naming Convention

```
describe('ComponentName', () => {
  describe('methodName', () => {
    it('should [expected behavior] when [condition]', () => {
      // test implementation
    });
  });
});
```

**Good Examples:**
- `should return null when user is not found`
- `should throw ValidationError when email format is invalid`
- `should calculate total price including tax when tax rate is provided`

**Bad Examples:**
- `test1` (무의미한 이름)
- `it works` (기대 동작 불명확)
- `should test the method` (무엇을 검증하는지 불명확)

### Test Organization Patterns

#### 1. Co-location Pattern
```
src/
  components/
    Button.tsx
    Button.test.tsx      # 같은 디렉토리에 위치
    Button.spec.tsx      # 또는 .spec 사용
```

#### 2. Mirror Pattern
```
src/
  components/
    Button.tsx
tests/
  components/
    Button.test.tsx      # 디렉토리 구조 미러링
```

#### 3. Test Type Separation
```
tests/
  unit/
    components/
      Button.test.tsx
  integration/
    api/
      users.test.tsx
  e2e/
    flows/
      checkout.test.tsx
```

## References

이 스킬은 다음 레퍼런스 파일을 제공합니다:

### 1. Test Patterns (`references/test-patterns.md`)

**내용:**
- 테스트 피라미드 상세 설명
- 유닛 테스트 패턴 (Given-When-Then, Test Doubles, Builder Pattern)
- 통합 테스트 패턴 (Database, API, Service Integration)
- E2E 테스트 패턴 (Page Object Model, State Management)
- 프레임워크별 Quick Reference (Jest, Vitest, JUnit, pytest, Go)
- 테스트 안티패턴 및 해결책

**활용 시점:**
- 테스트 코드 작성 시 패턴 참조
- Mock/Stub 사용법 확인
- 프레임워크별 문법 Quick Reference
- Code review 시 안티패턴 식별

### 2. Coverage Guide (`references/coverage-guide.md`)

**내용:**
- 커버리지 메트릭 종류 및 목표치 (Statement, Branch, Function, Line)
- 커버리지 분석 워크플로우
- 테스트 케이스 설계 기법 (Equivalence Partitioning, Boundary Value Analysis)
- 프레임워크별 커버리지 명령어
- 테스트 우선순위 결정 가이드

**활용 시점:**
- 커버리지 리포트 분석 시
- 테스트 케이스 설계 시
- CI/CD 커버리지 임계값 설정
- 테스트 우선순위 결정

## Related Agents

이 스킬과 함께 사용하면 효과적인 에이전트:

- **qa-engineer**: 테스트 전략 수립 및 테스트 케이스 설계 전문
- **code-reviewer**: 테스트 코드 품질 검토 및 개선 제안
- **refactor-specialist**: 리팩토링 시 테스트 안정성 확보
- **ci-cd-engineer**: CI/CD 파이프라인에 테스트 통합

## Quick Start Examples

### 예제 1: Jest Unit Test with Mocking

```typescript
// userService.test.ts
import { UserService } from './userService';
import { UserRepository } from './userRepository';

jest.mock('./userRepository');

describe('UserService', () => {
  let service: UserService;
  let mockRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepository = new UserRepository() as jest.Mocked<UserRepository>;
    service = new UserService(mockRepository);
  });

  describe('getUserById', () => {
    it('should return user when user exists', async () => {
      // Given
      const userId = '123';
      const expectedUser = { id: userId, name: 'John' };
      mockRepository.findById.mockResolvedValue(expectedUser);

      // When
      const result = await service.getUserById(userId);

      // Then
      expect(result).toEqual(expectedUser);
      expect(mockRepository.findById).toHaveBeenCalledWith(userId);
    });

    it('should throw NotFoundError when user does not exist', async () => {
      // Given
      const userId = 'nonexistent';
      mockRepository.findById.mockResolvedValue(null);

      // When & Then
      await expect(service.getUserById(userId))
        .rejects.toThrow('User not found');
    });
  });
});
```

### 예제 2: Integration Test with Test Container

```typescript
// userApi.integration.test.ts
import request from 'supertest';
import { app } from './app';
import { setupTestDatabase, teardownTestDatabase } from './testUtils';

describe('User API Integration Tests', () => {
  beforeAll(async () => {
    await setupTestDatabase();
  });

  afterAll(async () => {
    await teardownTestDatabase();
  });

  describe('POST /api/users', () => {
    it('should create user and return 201', async () => {
      // Given
      const newUser = {
        email: 'test@example.com',
        name: 'Test User'
      };

      // When
      const response = await request(app)
        .post('/api/users')
        .send(newUser)
        .expect(201);

      // Then
      expect(response.body).toMatchObject({
        email: newUser.email,
        name: newUser.name
      });
      expect(response.body.id).toBeDefined();
    });
  });
});
```

## Best Practices Summary

1. **테스트 피라미드 준수**: 유닛 테스트 70%, 통합 테스트 20%, E2E 테스트 10%
2. **독립성 유지**: 각 테스트는 독립적으로 실행 가능해야 함
3. **명확한 네이밍**: 테스트 이름만으로 의도 파악 가능하도록
4. **AAA 패턴**: Given-When-Then 구조로 일관성 유지
5. **적절한 Mocking**: 경계에서만 mock 사용, 과도한 mocking 지양
6. **커버리지 목표**: 80-85% 목표, 100% 추구하지 않음
7. **빠른 실행**: 전체 테스트 스위트 5분 이내 실행 목표
8. **CI/CD 통합**: 모든 커밋/PR에서 자동 테스트 실행

## Common Pitfalls

1. **Implementation Testing**: 내부 구현 대신 동작(behavior) 테스트
2. **Shared State**: 테스트 간 상태 공유로 인한 flaky test
3. **Sleep/Timeout**: 고정 대기 대신 polling/waitFor 사용
4. **No Assertion**: 테스트가 항상 통과하는 문제
5. **Too Much Mocking**: 실제 동작과 동떨어진 테스트

## Conclusion

효과적인 테스트 전략은 속도와 신뢰성의 균형입니다. 이 스킬의 레퍼런스를 활용하여 프로젝트에 맞는 최적의 테스트 전략을 수립하고, 일관성 있는 테스트 코드를 작성하세요.

**핵심 기억 사항:**
- 테스트는 비용이 아닌 투자
- 빠른 피드백 루프가 생산성의 핵심
- 테스트 코드도 프로덕션 코드만큼 중요하게 관리
- 100% 커버리지보다 핵심 로직의 충실한 검증이 우선
