# Claude Code 슬래시 명령어 공식 문서

> 원본: https://code.claude.com/docs/ko/slash-commands
> 최종 업데이트: 2026-01-26

---

# 슬래시 명령어

> 대화형 세션 중에 슬래시 명령어를 사용하여 Claude의 동작을 제어합니다.

## 기본 제공 슬래시 명령어

| 명령어                       | 목적                                    |
| :------------------------ | :------------------------------------ |
| `/add-dir`                | 추가 작업 디렉토리 추가                         |
| `/agents`                 | 특화된 작업을 위한 사용자 정의 AI 서브에이전트 관리        |
| `/bashes`                 | 백그라운드 작업 나열 및 관리                      |
| `/bug`                    | 버그 보고 (Anthropic에 대화 전송)              |
| `/clear`                  | 대화 기록 삭제                              |
| `/compact [instructions]` | 선택적 포커스 지침을 포함한 대화 압축                 |
| `/config`                 | 설정 인터페이스 열기                           |
| `/context`                | 현재 컨텍스트 사용량을 색상 그리드로 시각화              |
| `/cost`                   | 토큰 사용 통계 표시                           |
| `/doctor`                 | Claude Code 설치 상태 확인                  |
| `/exit`                   | REPL 종료                               |
| `/export [filename]`      | 현재 대화를 파일 또는 클립보드로 내보내기               |
| `/help`                   | 사용 도움말 받기                             |
| `/hooks`                  | 도구 이벤트에 대한 훅 구성 관리                    |
| `/ide`                    | IDE 통합 관리 및 상태 표시                     |
| `/init`                   | `CLAUDE.md` 가이드로 프로젝트 초기화             |
| `/login`                  | Anthropic 계정 전환                       |
| `/logout`                 | Anthropic 계정에서 로그아웃                   |
| `/mcp`                    | MCP 서버 연결 및 OAuth 인증 관리               |
| `/memory`                 | `CLAUDE.md` 메모리 파일 편집                 |
| `/model`                  | AI 모델 선택 또는 변경                        |
| `/permissions`            | 권한 보기 또는 업데이트                         |
| `/plan`                   | 프롬프트에서 직접 계획 모드 진입                    |
| `/plugin`                 | Claude Code 플러그인 관리                   |
| `/resume [session]`       | ID 또는 이름으로 대화 재개하거나 세션 선택기 열기         |
| `/review`                 | 코드 검토 요청                              |
| `/vim`                    | vim 모드 진입                             |

## 사용자 정의 슬래시 명령어

사용자 정의 슬래시 명령어를 사용하면 자주 사용하는 프롬프트를 Markdown 파일로 정의하여 Claude Code가 실행할 수 있습니다.

### 구문

```
/<command-name> [arguments]
```

### 명령어 유형

#### 프로젝트 명령어

리포지토리에 저장되고 팀과 공유되는 명령어입니다.

**위치**: `.claude/commands/`

```bash
# 프로젝트 명령어 생성
mkdir -p .claude/commands
echo "Analyze this code for performance issues and suggest optimizations:" > .claude/commands/optimize.md
```

#### 개인 명령어

모든 프로젝트에서 사용 가능한 명령어입니다.

**위치**: `~/.claude/commands/`

```bash
# 개인 명령어 생성
mkdir -p ~/.claude/commands
echo "Review this code for security vulnerabilities:" > ~/.claude/commands/security-review.md
```

### 기능

#### 네임스페이싱

관련 명령어를 그룹화하려면 하위 디렉토리를 사용하세요:

* `.claude/commands/frontend/component.md`는 설명이 "(project:frontend)"인 `/component`를 생성합니다
* `~/.claude/commands/component.md`는 설명이 "(user)"인 `/component`를 생성합니다

#### 인수

##### `$ARGUMENTS`를 사용한 모든 인수

```bash
# 명령어 정의
echo 'Fix issue #$ARGUMENTS following our coding standards' > .claude/commands/fix-issue.md

# 사용
> /fix-issue 123 high-priority
# $ARGUMENTS는 "123 high-priority"가 됩니다
```

##### `$1`, `$2` 등을 사용한 개별 인수

```bash
# 명령어 정의
echo 'Review PR #$1 with priority $2 and assign to $3' > .claude/commands/review-pr.md

# 사용
> /review-pr 456 high alice
# $1은 "456", $2는 "high", $3은 "alice"가 됩니다
```

#### Bash 명령어 실행

`!\` 접두사를 사용하여 슬래시 명령어가 실행되기 전에 bash 명령어를 실행합니다:

\```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
description: Create a git commit
---

## Context

- Current git status: !\`git status\`
- Current git diff (staged and unstaged changes): !\`git diff HEAD\`
- Current branch: !\`git branch --show-current\`
- Recent commits: !\`git log --oneline -10\`

## Your task

Based on the above changes, create a single git commit.
```

#### 파일 참조

`@` 접두사를 사용하여 명령어에 파일 내용을 포함합니다:

```markdown
# 특정 파일 참조

Review the implementation in @src/utils/helpers.js

# 여러 파일 참조

Compare @src/old-version.js with @src/new-version.js
```

### 프론트매터

| 프론트매터                      | 목적                       | 기본값             |
| :------------------------- | :----------------------- | :-------------- |
| `allowed-tools`            | 명령어가 사용할 수 있는 도구 목록      | 대화에서 상속됨        |
| `argument-hint`            | 슬래시 명령어에 필요한 인수 힌트       | 없음              |
| `description`              | 명령어에 대한 간단한 설명           | 프롬프트의 첫 번째 줄 사용 |
| `model`                    | 특정 모델 문자열                | 대화에서 상속됨        |
| `disable-model-invocation` | Skill 도구가 호출하는 것을 방지할지 여부 | false           |
| `hooks`                    | 이 명령어의 실행 범위로 훅을 정의      | 없음              |

예:

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
argument-hint: [message]
description: Create a git commit
model: claude-3-5-haiku-20241022
---

Create a git commit with message: $ARGUMENTS
```

#### 명령어에 대한 훅 정의

```markdown
---
description: Deploy to staging with validation
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-deploy.sh"
          once: true
---

Deploy the current branch to staging environment.
```

## 플러그인 명령어

플러그인은 Claude Code와 원활하게 통합되는 사용자 정의 슬래시 명령어를 제공할 수 있습니다.

### 플러그인 명령어 작동 방식

* **네임스페이스됨**: 명령어는 `/plugin-name:command-name` 형식을 사용
* **자동으로 사용 가능**: 플러그인이 설치되고 활성화되면 해당 명령어가 `/help`에 나타남
* **완전히 통합됨**: 모든 명령어 기능을 지원 (인수, 프론트매터, bash 실행, 파일 참조)

### 호출 패턴

```shell
# 직접 명령어 (충돌이 없을 때)
/command-name

# 플러그인 접두사 (명확히 하기 위해 필요할 때)
/plugin-name:command-name

# 인수 포함
/command-name arg1 arg2
```

## MCP 슬래시 명령어

MCP 서버는 프롬프트를 슬래시 명령어로 노출할 수 있습니다:

```
/mcp__<server-name>__<prompt-name> [arguments]
```

### MCP 연결 관리

`/mcp` 명령어를 사용하여:

* 구성된 모든 MCP 서버 보기
* 연결 상태 확인
* OAuth 지원 서버로 인증
* 각 서버의 사용 가능한 도구 및 프롬프트 보기

## `Skill` 도구

`Skill` 도구를 사용하면 Claude가 대화 중에 사용자 정의 슬래시 명령어 및 에이전트 스킬을 프로그래밍 방식으로 호출할 수 있습니다.

### `Skill` 도구가 호출할 수 있는 것

| 유형             | 위치                                           | 요구사항                                    |
| :------------- | :------------------------------------------- | :-------------------------------------- |
| 사용자 정의 슬래시 명령어 | `.claude/commands/` 또는 `~/.claude/commands/` | `description` 프론트매터가 있어야 함              |
| 에이전트 스킬        | `.claude/skills/` 또는 `~/.claude/skills/`     | `disable-model-invocation: true`가 없어야 함 |

### Claude가 특정 명령어를 사용하도록 권장

```
> Run /write-unit-test when you are about to start writing tests.
```

### `Skill` 도구 비활성화

```bash
/permissions
# 거부 규칙에 추가: Skill
```

### `Skill` 권한 규칙

* **정확한 일치**: `Skill(/commit)` (인수 없이 `/commit`만 허용)
* **접두사 일치**: `Skill(/review-pr:*)` (모든 인수를 포함한 `/review-pr` 허용)

### 문자 예산 제한

* **기본 제한**: 15,000자
* **사용자 정의 제한**: `SLASH_COMMAND_TOOL_CHAR_BUDGET` 환경 변수를 통해 설정

## 스킬 대 슬래시 명령어

### 슬래시 명령어 사용 대상

**빠르고 자주 사용하는 프롬프트**:
* 자주 사용하는 간단한 프롬프트 스니펫
* 빠른 미리 알림 또는 템플릿
* 한 파일에 맞는 자주 사용하는 지침

**예제**:
* `/review` → "Review this code for bugs and suggest improvements"
* `/explain` → "Explain this code in simple terms"
* `/optimize` → "Analyze this code for performance issues"

### 스킬 사용 대상

**구조가 있는 포괄적인 기능**:
* 여러 단계가 있는 복잡한 워크플로우
* 스크립트 또는 유틸리티가 필요한 기능
* 여러 파일에 걸쳐 구성된 지식
* 표준화하려는 팀 워크플로우

**예제**:
* 양식 채우기 스크립트 및 검증이 있는 PDF 처리 스킬
* 다양한 데이터 유형에 대한 참조 문서가 있는 데이터 분석 스킬
* 스타일 가이드 및 템플릿이 있는 문서 스킬

### 주요 차이점

| 측면      | 슬래시 명령어             | 에이전트 스킬                 |
| ------- | ------------------- | ----------------------- |
| **복잡성** | 간단한 프롬프트            | 복잡한 기능                  |
| **구조**  | 단일 .md 파일           | SKILL.md + 리소스가 있는 디렉토리 |
| **발견**  | 명시적 호출 (`/command`) | 자동 (컨텍스트 기반)            |
| **파일**  | 한 파일만               | 여러 파일, 스크립트, 템플릿        |
| **범위**  | 프로젝트 또는 개인          | 프로젝트 또는 개인              |

### 각각을 사용할 때

**슬래시 명령어 사용**:
* 같은 프롬프트를 반복적으로 호출합니다
* 프롬프트가 한 파일에 맞습니다
* 실행 시기를 명시적으로 제어하려고 합니다

**스킬 사용**:
* Claude가 기능을 자동으로 발견해야 합니다
* 여러 파일 또는 스크립트가 필요합니다
* 검증 단계가 있는 복잡한 워크플로우
* 팀이 표준화되고 상세한 지침이 필요합니다

## 참고 항목

* **플러그인** - 플러그인을 통해 사용자 정의 명령어로 Claude Code 확장
* **ID 및 액세스 관리** - MCP 도구 권한을 포함한 권한에 대한 완전한 가이드
* **대화형 모드** - 바로 가기, 입력 모드 및 대화형 기능
* **CLI 참조** - 명령줄 플래그 및 옵션
* **설정** - 구성 옵션
