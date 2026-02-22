---
name: setup
description: "oh-my-speckit 대화형 설정 위자드. 전제조건 확인, 스폰 모드, 윈도우 모드 설정."
argument-hint: ""
allowed-tools: Bash, Read, Write, Glob, AskUserQuestion
---

# /oh-my-speckit:setup - Setup Wizard

oh-my-speckit 플러그인 대화형 설정 위자드.

---

## Step 1: 프로젝트 루트 탐색

cwd부터 상위로 올라가며 탐색:
1. `.specify/` - 기존 폴더가 있으면 **최우선**
2. `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`
3. `.git/` - 최후의 fallback

```
AskUserQuestion:
- question: "프로젝트 루트가 [탐색 경로]이 맞나요?"
- header: "프로젝트"
- options:
  - label: "예, 맞습니다 (권장)"
    description: "이 경로를 프로젝트 루트로 사용합니다"
  - label: "다른 경로 지정"
    description: "직접 프로젝트 루트 경로를 입력합니다"
```

탐색된 경로를 `PROJECT_ROOT`로 저장.

---

## Step 2: 전제조건 확인

아래 항목을 **순서대로 Bash로 확인**하고, 결과를 내부적으로 기록합니다.

### 2-1. tmux 설치

```
Bash: which tmux
```

- 찾으면 → `Bash: tmux -V` → 버전 기록, 상태 = OK
- 못 찾으면 → 상태 = FAIL

### 2-2. tmux 세션 확인

```
Bash: echo "$TMUX"
```

- 출력 있음 → 상태 = OK (tmux 세션 안에서 실행 중)
- 출력 없음 → 상태 = WARN (tmux 세션 밖에서 실행 중 — 경고만, 차단 아님)

### 2-3. Claude CLI 확인

```
Bash: which claude
```

- 찾으면 → 상태 = OK
- 못 찾으면 → 상태 = FAIL

### 2-4. Agent Teams 환경변수 확인

```
Bash: echo "$CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"
```

- `1`이면 → 상태 = OK
- 아니면 → 상태 = WARN

### 전제조건 결과 표시

```markdown
## 전제조건 확인

| 항목 | 상태 | 비고 |
|------|------|------|
| tmux | {OK/FAIL} | {버전 또는 "미설치 — `brew install tmux` 또는 `apt install tmux`"} |
| tmux 세션 | {OK/WARN} | {세션 안/밖} |
| Claude CLI | {OK/FAIL} | {경로 또는 "미설치"} |
| Agent Teams | {OK/WARN} | {"활성화" 또는 "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 설정 필요"} |
```

<instructions>
- FAIL 항목이 있으면 해결 방법을 안내합니다.
- tmux FAIL: OS에 맞는 설치 명령을 안내합니다 (`brew install tmux`, `sudo apt install tmux` 등).
- Claude CLI FAIL: `npm install -g @anthropic-ai/claude-code` 안내.
- Agent Teams WARN: `~/.claude/settings.json`의 `env`에 `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"` 추가 안내.
- WARN만 있고 FAIL이 없으면 계속 진행합니다.
- FAIL이 있어도 계속 진행은 가능하지만, 해당 기능 사용 시 문제가 될 수 있음을 알립니다.
</instructions>

---

## Step 3: 기존 설정 확인

```
Read tool: ${PROJECT_ROOT}/.specify/config.json
```

<instructions>
- 파일이 존재하면 기존 값을 파싱하여 현재 설정으로 표시합니다:
  ```markdown
  기존 설정이 발견되었습니다:
  - 스폰 모드: {spawnGpt ? "GPT 모드" : "Claude 모드"}
  - 배치 모드: {spawnWindow ? "별도 윈도우" : "같은 윈도우"}
  ```
  이 값들을 아래 Step 4, 5에서 기본 선택(권장)으로 반영합니다.
- 파일이 없으면 기본값(`spawnGpt: false`, `spawnWindow: false`)으로 진행합니다.
</instructions>

---

## Step 4: 스폰 모드 설정 (spawnGpt)

```
AskUserQuestion:
- question: "팀메이트를 어떤 모델로 실행할까요?"
- header: "스폰 모드"
- options:
  - label: "Claude 모드 (권장)"
    description: "Claude CLI 네이티브 에이전트. 별도 설정 없이 바로 사용 가능"
  - label: "GPT 모드"
    description: "cli-proxy-api를 통해 GPT 모델 사용 (별도 설정 필요)"
```

<instructions>
- 기존 config에 `spawnGpt: true`가 설정되어 있으면, "GPT 모드"를 권장 옵션으로 변경합니다.
- Claude 선택 → `spawnGpt = false`
- GPT 선택 → `spawnGpt = true`

**GPT 모드 선택 시 추가 확인:**

```
Bash: which cli-proxy-api 2>/dev/null; echo "---"; which gpt-claude-code 2>/dev/null
```

확인 결과를 안내:
- cli-proxy-api 미설치 → `npm install -g cli-proxy-api` 안내
- gpt-claude-code 미설치 → `npm install -g gpt-claude-code` 안내
- 둘 다 설치됨 → "GPT 모드 전제조건 확인 완료" 표시
</instructions>

---

## Step 5: 윈도우 모드 설정 (spawnWindow)

```
AskUserQuestion:
- question: "팀메이트 배치 방식을 선택해주세요."
- header: "배치 모드"
- options:
  - label: "같은 윈도우 (권장)"
    description: "리더 윈도우에 pane 분할로 배치. 한 화면에서 모든 팀메이트 확인"
  - label: "별도 윈도우"
    description: "팀메이트를 별도 tmux 윈도우에 배치. 화면이 넓을 때 유용"
```

<instructions>
- 기존 config에 `spawnWindow: true`가 설정되어 있으면, "별도 윈도우"를 권장 옵션으로 변경합니다.
- 같은 윈도우 선택 → `spawnWindow = false`
- 별도 윈도우 선택 → `spawnWindow = true`
</instructions>

---

## Step 6: 저장

<instructions>

**디렉토리 생성:**

```
Bash: mkdir -p ${PROJECT_ROOT}/.specify/memory && mkdir -p ${PROJECT_ROOT}/.specify/specs
```

**config.json 저장:**

```
Write tool:
- file_path: ${PROJECT_ROOT}/.specify/config.json
- content: {spawnGpt, spawnWindow 값을 포함한 JSON}
```

JSON 형식:
```json
{
  "spawnGpt": false,
  "spawnWindow": false
}
```

- 기존 config.json이 있고 추가 필드가 있었다면, 해당 필드를 유지하면서 `spawnGpt`와 `spawnWindow`만 업데이트합니다.

</instructions>

---

## Step 7: 요약 + 다음 단계 안내

```markdown
## oh-my-speckit Setup 완료

| 항목 | 상태 |
|------|------|
| 프로젝트 루트 | {PROJECT_ROOT} |
| tmux | {OK — 버전 / FAIL — 미설치} |
| tmux 세션 | {OK / WARN — 세션 밖} |
| Claude CLI | {OK / FAIL — 미설치} |
| Agent Teams | {OK / WARN — 미설정} |
| 스폰 모드 | {Claude 모드 / GPT 모드} |
| 배치 모드 | {같은 윈도우 / 별도 윈도우} |

### 설정 파일
- `{PROJECT_ROOT}/.specify/config.json`

### 다음 단계
1. 프로젝트 원칙 분석: `/oh-my-speckit:constitution`
2. 기능 스펙 작성: `/oh-my-speckit:specify [기능 설명]`
3. 설정 변경: `/oh-my-speckit:setup`
```
