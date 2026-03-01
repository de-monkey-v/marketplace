---
name: spec-writing
description: This skill should be used when the user asks to "스펙 작성", "스펙 작성해줘", "요구사항 정리", "기능 정의", "spec 작성", or mentions writing specifications. Provides knowledge for converting feature requests into structured spec documents.
version: 1.1.0
---

# Specify

자연어 기능 설명을 구조화된 요구사항으로 변환하는 지식 가이드.
산출물은 **plan.md의 Part 1: Specification** 섹션으로 통합됩니다.

**Note:** 이 스킬의 지식은 specify 커맨드의 리더와 researcher 팀메이트가 참조합니다.

## 워크플로우 위치

```
specify → implement → verify
↑ 현재
```

## 개요

| 항목 | 값 |
|------|-----|
| **입력** | 기능 요청 (자연어) |
| **출력** | `.specify/specs/{id}/plan.md` (Part 1: Specification) |

## 핵심 Phase

| Phase | 내용 | 사용자 승인 |
|-------|------|------------|
| 0 | 프로젝트 루트 확인 | ✅ 위치 확인 |
| 1.5 | 기술 스택 결정 | ✅ 스택 선택 |
| 2 | 조사 및 접근방식 제안 | ✅ 방향 승인 |
| 2.5 | 기존 시스템 영향 분석 | ✅ 호환성 선택 |
| 3 | 요구사항 분석 | - |
| 5 | plan.md Part 1 작성 | - |

## plan.md Part 1 핵심 구조

```markdown
# Plan: [기능명]

## Part 1: Specification

### 메타데이터
- ID: NNN-feature-name
- Status: Draft | Review | Approved
- Priority: P0 | P1 | P2

### 요청 이력
#### 최초 요청
> [원문]

### 사용자 스토리
- US-001: As a [user], I want [goal] so that [benefit]

### 기능 요구사항 (FR)
- FR-001: [검증 가능한 요구사항] | AC: [합격 기준]

### 비기능 요구사항 (NFR)
- NFR-001: [측정 가능한 기준]

### 엣지 케이스
- EC-001: [경계 조건]

### 기술 결정 (Technical Decisions)
| ID | 결정 항목 | 선택 | 근거 | 결정일 |

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

## AC(합격 기준) 가이드

각 FR에는 반드시 AC(Acceptance Criteria)를 포함합니다.

| 원칙 | 설명 |
|------|------|
| 구체적 | 입력 → 동작 → 기대 결과 |
| 검증 가능 | 코드/테스트로 확인 가능 |
| FR당 1-3개 | 너무 많으면 FR 분리 |

AC는 implement 단계에서 developer의 자가 검증 기준이 되고, qa의 요구사항 충족 검증 기준이 됩니다.

## 호환성 옵션 (Phase 2.5)

| 옵션 | 설명 | 선택 기준 |
|------|------|----------|
| A: 하위 호환성 | 기존 API 유지, optional 필드 추가 | 기존 클라이언트 영향 최소화 |
| B: V2 분리 | 새 API 엔드포인트 | 구조적 변경 필요 |
| C: Breaking Change | 기존 API 직접 수정 | 마이그레이션 가능할 때 |

## 재진입

**Verify에서 "스펙 불명확" 실패 시:**

```
verify 실패 → specify 재진입
  1. 기존 plan.md 로드
  2. Part 1의 불명확한 부분 식별
  3. 사용자와 명확화
  4. 수정 이력 기록
  5. plan.md Part 1 업데이트
```

## 디렉토리 구조

```
.specify/
├── memory/
│   └── constitution.md
└── specs/
    └── {id}/
        └── plan.md  ← 산출물 (Part 1: Specification + Part 2: Implementation Plan)
```

## 다음 단계

```
✅ Spec 완료 → /oh-my-speckit:implement {spec-id}
```

## 참고 자료

| 파일 | 설명 |
|------|------|
| `references/workflow-detail.md` | Phase별 상세 절차 |
| `../plan-writing/references/plan-template.md` | 통합 Plan 문서 전체 템플릿 |
