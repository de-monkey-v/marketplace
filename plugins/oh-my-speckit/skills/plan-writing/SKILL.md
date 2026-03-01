---
name: plan-writing
description: This skill should be used when the user asks to "설계해줘", "설계", "구현 계획", "plan 작성", "plan.md 작성", "plan 만들어", "아키텍처 설계", "아키텍처 계획", "design plan", "create plan", or mentions creating implementation plans from spec. Provides knowledge for analyzing codebase and creating plan.md from spec.
version: 1.1.0
---

# Design

기능 요청을 분석하고, 요구사항 정의(Part 1)와 구현 계획(Part 2)을 하나의 plan.md로 작성하는 지식 가이드.

**Note:** 이 스킬은 specify 커맨드에서 plan 작성 시 리더와 explorer/analyst 팀메이트가 참조합니다.

## 워크플로우 위치

```
specify → implement → verify
↑ 현재 (plan 작성)
```

## 개요

| 항목 | 값 |
|------|-----|
| **입력** | 기능 요청 (자연어) + 코드베이스 분석 결과 |
| **출력** | `.specify/specs/{id}/plan.md` |
| **핵심 팀메이트** | explorer, analyst |

## 통합 plan.md 구조

plan.md는 **Part 1: Specification**(요구사항)과 **Part 2: Implementation Plan**(구현 계획)을 하나로 통합합니다.

```markdown
# Plan: [기능명]

## Part 1: Specification
### 메타데이터
### 요청 이력
### 개요
### 아키텍처 컨텍스트
### 사용자 스토리 (US)
### 기능 요구사항 (FR) -- AC 포함
### 비기능 요구사항 (NFR)
### 엣지 케이스 (EC)
### 기술 결정 (TD)
### 기술 스택 결정
### 제약 조건
### 구현 범위 제한 (YAGNI)

## Part 2: Implementation Plan
### 코드베이스 분석 결과
### 재사용 분석
### FR 매핑
### 변경 파일
### Breaking Change (해당시)
### E2E 테스트 시나리오
### 구현 단계 (Phase별 체크박스)
### 검증 기준
```

## 핵심 Phase

| Phase | 내용 | 사용자 승인 |
|-------|------|------------|
| 1 | 요구사항 분석 + 기능 파싱 | - |
| **1.5** | **기술 결정 파싱 + 기술 스택 결정** | - |
| 2 | Constitution 확인 | - |
| 3 | 코드베이스 분석 (팀메이트) | - |
| 3.5 | Breaking Change 분석 | ✅ 설계 방향 (기술 결정에 없을 때만) |
| 4 | Plan 작성 (팀메이트) | ✅ Plan 초안 |
| 5.5 | Plan 정합성 검증 | - |

## 기술 결정 파싱 (Phase 1.5)

**목적**: specify 단계에서 결정된 사항을 파싱하여 중복 질문 방지

**파싱 대상:**
```markdown
## 기술 결정 (Technical Decisions)

| ID | 결정 항목 | 선택 | 근거 | 결정일 |
|----|----------|------|------|--------|
| TD-1 | API 버전 전략 | V2 신규 생성 | ... | ... |
```

**조건부 질문 스킵:**
- `API 버전 전략` 결정 있음 → Breaking Change 질문 건너뛰기
- `아키텍처 패턴` 결정 있음 → DDD 질문 건너뛰기
- `인증 방식` 결정 있음 → 인증 방식 질문 건너뛰기

## 기술 스택 결정 파싱 (Phase 1.5)

**목적**: specify 단계에서 WebSearch를 통해 조사하고 결정된 기술 스택을 plan.md에 반영

**파싱 대상:**
```markdown
### 기술 스택 결정

#### 프론트엔드
| 후보 | GitHub Stars | npm weekly | 최신 버전 | 성숙도 | 선택 |

#### 백엔드
| 후보 | GitHub Stars | 최신 버전 | 생태계 | 성숙도 | 선택 |

#### 데이터베이스 / ORM
| 영역 | 선택 | 버전 | 근거 |

#### 아키텍처 패턴
| 항목 | 선택 | 근거 |
```

## 설계 방향 (Phase 2.5)

### 최소 변경 원칙

| 상황 | 권장 접근법 |
|------|-----------|
| 기능 추가 | 새 함수/클래스 생성 |
| 기능 변경 | 래퍼 함수로 확장 |
| 버그 수정 | 최소 범위 수정 |

### 옵션

| 방향 | 설명 |
|------|------|
| A: 확장 중심 | 기존 코드 수정 최소화 (권장) |
| B: 리팩토링 포함 | 기존 코드 개선 함께 |
| C: V2 분리 | Breaking Change 시 |

## 검증 기준 설계 원칙

plan.md의 검증 기준은 implement에서 developer/qa가 직접 사용하는 판단 기준입니다.

| 원칙 | 설명 |
|------|------|
| FR별 구조화 | 각 FR의 AC를 plan에 인용하여 추적 가능 |
| 검증 방법 명시 | 단위/통합/E2E/수동 중 구체적 방법 기재 |
| Phase 연결 | 체크박스에 FR 번호 주석으로 추적성 확보 |

이를 통해 implement 단계에서:
- developer가 체크박스 완료 시 해당 FR/AC 충족 여부를 자가 확인
- qa가 FR 매핑 기반으로 요구사항 충족을 체계적으로 검증

## 재진입

**Verify에서 "plan.md 누락" 실패 시:**

```
verify 실패 → specify 재진입 (plan 작성)
  1. 기존 plan.md 로드
  2. 미충족 FR 식별
  3. plan.md 보완
  4. implement로 안내
```

## 디렉토리 구조

```
.specify/specs/{id}/
└── plan.md   ← 산출물 (Part 1 + Part 2 통합)
```

## 다음 단계

```
✅ Design 완료 → /oh-my-speckit:implement {spec-id}
```

## 참고 자료

| 파일 | 설명 |
|------|------|
| `references/plan-template.md` | 통합 Plan 문서 전체 템플릿 |
| `references/workflow-detail.md` | Phase별 상세 절차 |
