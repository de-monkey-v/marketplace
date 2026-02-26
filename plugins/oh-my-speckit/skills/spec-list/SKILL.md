---
name: spec-list
description: This skill should be used when the user asks to "스펙 리스트", "스펙 목록", "스펙 확인", "스펙 보여줘", "list specs", "show specs", "view specs", "what specs exist", or mentions viewing/listing/checking existing spec files.
user-invocable: true
---

# Spec List

프로젝트의 `.specify/specs/` 디렉토리에 있는 모든 스펙 파일을 조회하여 표시한다.

## 워크플로우 위치

```
specify → implement → verify
  ↑ spec-list (조회 전용)
```

## 실행 절차

### Step 1: 프로젝트 루트 탐색

cwd부터 상위로 올라가며 탐색:
1. `.specify/` - 기존 폴더가 있으면 최우선
2. `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`
3. `.git/` - 최후의 fallback

탐색된 경로를 `PROJECT_ROOT`로 사용.

### Step 2: 스크립트 실행

```
Bash tool:
- command: bash ${CLAUDE_PLUGIN_ROOT}/scripts/list-specs.sh "${PROJECT_ROOT}"
```

스크립트가 `.specify/specs/` 내의 모든 스펙 디렉토리를 스캔하고 포맷된 테이블을 출력한다.

### Step 3: 결과 표시

스크립트 출력을 사용자에게 그대로 표시한다.

### Step 4: 다음 액션 안내

결과와 함께 다음 액션을 안내:

| 상황 | 안내 |
|------|------|
| 스펙이 있을 때 | "특정 스펙의 상세 내용을 보려면 spec ID를 알려주세요" |
| 스펙이 있을 때 | 구현: `/oh-my-speckit:implement {spec-id}` |
| 스펙이 있을 때 | 검증: `/oh-my-speckit:verify {spec-id}` |
| 스펙이 없을 때 | 새 스펙 생성: `/oh-my-speckit:specify [기능 설명]` |

### Step 5: 특정 스펙 상세 조회 (선택)

사용자가 특정 spec ID를 언급하면:

```
Read tool:
- file_path: ${PROJECT_ROOT}/.specify/specs/{spec-id}/spec.md
```

spec.md의 주요 섹션을 요약하여 표시:
- 메타데이터 (ID, Status, Priority)
- 개요
- 사용자 스토리 수
- 기능 요구사항 수 (P1/P2 구분)
- 기술 결정 사항

plan.md가 존재하면 Plan 요약도 함께 표시.

## 에러 처리

| 상황 | 처리 |
|------|------|
| PROJECT_ROOT 탐지 실패 | 사용자에게 프로젝트 경로를 직접 지정하도록 안내 |
| .specify 디렉토리 없음 | `/oh-my-speckit:setup` 또는 `/oh-my-speckit:specify` 안내 |
| 스크립트 실행 실패 | 에러 메시지 표시 후 수동 확인 방법 안내 |
