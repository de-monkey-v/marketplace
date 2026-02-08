# Claude Code 플러그인 생성 공식 문서

> 원본: https://code.claude.com/docs/ko/plugins
> 최종 업데이트: 2026-01-26

---

# 플러그인 만들기

> 슬래시 명령어, 에이전트, 훅, 스킬 및 MCP 서버를 사용하여 Claude Code를 확장하는 사용자 정의 플러그인을 만듭니다.

플러그인을 사용하면 프로젝트와 팀 전체에서 공유할 수 있는 사용자 정의 기능으로 Claude Code를 확장할 수 있습니다.

## 플러그인 대 독립 실행형 구성을 사용할 때

| 접근 방식                                            | 슬래시 명령어 이름           | 최적 용도                                   |
| :----------------------------------------------- | :------------------- | :-------------------------------------- |
| **독립 실행형** (`.claude/` 디렉토리)                     | `/hello`             | 개인 워크플로우, 프로젝트별 사용자 정의, 빠른 실험           |
| **플러그인** (`.claude-plugin/plugin.json`이 있는 디렉토리) | `/plugin-name:hello` | 팀원과 공유, 커뮤니티에 배포, 버전 관리 릴리스, 프로젝트 간 재사용 |

**독립 실행형 구성을 사용할 때**:
* 단일 프로젝트에 대해 Claude Code를 사용자 정의하는 경우
* 구성이 개인적이며 공유할 필요가 없는 경우
* `/hello` 또는 `/review`와 같은 짧은 슬래시 명령어 이름을 원하는 경우

**플러그인을 사용할 때**:
* 팀이나 커뮤니티와 기능을 공유하려는 경우
* 여러 프로젝트에서 동일한 슬래시 명령어/에이전트가 필요한 경우
* 마켓플레이스를 통해 배포하는 경우

## 빠른 시작

### 1. 플러그인 디렉토리 만들기

```bash
mkdir my-first-plugin
```

### 2. 플러그인 매니페스트 만들기

```bash
mkdir my-first-plugin/.claude-plugin
```

`my-first-plugin/.claude-plugin/plugin.json`:

```json
{
  "name": "my-first-plugin",
  "description": "A greeting plugin to learn the basics",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
```

| 필드            | 목적                                                 |
| :------------ | :------------------------------------------------- |
| `name`        | 고유 식별자 및 슬래시 명령어 네임스페이스 (예: `/my-first-plugin:hello`) |
| `description` | 플러그인 관리자에 표시                                       |
| `version`     | 의미 있는 버전 관리를 사용하여 릴리스 추적                            |
| `author`      | 선택 사항. 저작권 표시에 유용                                   |

### 3. 슬래시 명령어 추가

```bash
mkdir my-first-plugin/commands
```

`my-first-plugin/commands/hello.md`:

```markdown
---
description: Greet the user with a friendly message
---

# Hello Command

Greet the user warmly and ask how you can help them today.
```

### 4. 플러그인 테스트

```bash
claude --plugin-dir ./my-first-plugin
```

```shell
/my-first-plugin:hello
```

### 5. 슬래시 명령어 인수 추가

```markdown
---
description: Greet the user with a personalized message
---

# Hello Command

Greet the user named "$ARGUMENTS" warmly and ask how you can help them today.
```

```shell
/my-first-plugin:hello Alex
```

## 플러그인 구조 개요

> **일반적인 실수**: `commands/`, `agents/`, `skills/` 또는 `hooks/`를 `.claude-plugin/` 디렉토리 내에 넣지 마세요. `.claude-plugin/` 내에는 `plugin.json`만 들어갑니다.

| 디렉토리              | 위치      | 목적                              |
| :---------------- | :------ | :------------------------------ |
| `.claude-plugin/` | 플러그인 루트 | `plugin.json` 매니페스트만 포함 (필수)    |
| `commands/`       | 플러그인 루트 | Markdown 파일로 된 슬래시 명령어          |
| `agents/`         | 플러그인 루트 | 사용자 정의 에이전트 정의                  |
| `skills/`         | 플러그인 루트 | `SKILL.md` 파일이 있는 에이전트 스킬       |
| `hooks/`          | 플러그인 루트 | `hooks.json`의 이벤트 핸들러           |
| `.mcp.json`       | 플러그인 루트 | MCP 서버 구성                       |
| `.lsp.json`       | 플러그인 루트 | 코드 인텔리전스를 위한 LSP 서버 구성          |

## 더 복잡한 플러그인 개발

### 플러그인에 스킬 추가

플러그인 루트에 `skills/` 디렉토리를 추가하고 `SKILL.md` 파일을 포함:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── code-review/
        └── SKILL.md
```

각 `SKILL.md`는 `name` 및 `description` 필드가 있는 프론트매터와 그 뒤에 지침이 필요합니다:

```yaml
---
name: code-review
description: Reviews code for best practices and potential issues.
---

When reviewing code, check for:
1. Code organization and structure
2. Error handling
3. Security concerns
4. Test coverage
```

### 플러그인에 LSP 서버 추가

플러그인에 `.lsp.json` 파일을 추가:

```json
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}
```

### 플러그인을 로컬에서 테스트

```bash
claude --plugin-dir ./my-plugin
```

여러 플러그인을 로드하려면:

```bash
claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two
```

### 플러그인 문제 디버깅

1. **구조 확인**: 디렉토리가 플러그인 루트에 있고 `.claude-plugin/` 내부에 없는지 확인
2. **구성 요소를 개별적으로 테스트**: 각 명령어, 에이전트 및 훅을 별도로 확인
3. **검증 및 디버깅 도구 사용**: CLI 명령어 및 문제 해결 기법 사용

### 플러그인 공유

1. **문서 추가**: `README.md` 포함
2. **플러그인 버전 관리**: `plugin.json`에서 의미 있는 버전 관리 사용
3. **마켓플레이스 만들기 또는 사용**: 플러그인 마켓플레이스를 통해 배포

## 기존 구성을 플러그인으로 변환

### 마이그레이션 단계

#### 1. 플러그인 구조 만들기

```bash
mkdir -p my-plugin/.claude-plugin
```

`my-plugin/.claude-plugin/plugin.json`:

```json
{
  "name": "my-plugin",
  "description": "Migrated from standalone configuration",
  "version": "1.0.0"
}
```

#### 2. 기존 파일 복사

```bash
# Copy commands
cp -r .claude/commands my-plugin/

# Copy agents (if any)
cp -r .claude/agents my-plugin/

# Copy skills (if any)
cp -r .claude/skills my-plugin/
```

#### 3. 훅 마이그레이션

```bash
mkdir my-plugin/hooks
```

`my-plugin/hooks/hooks.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "npm run lint:fix $FILE" }]
      }
    ]
  }
}
```

#### 4. 마이그레이션된 플러그인 테스트

```bash
claude --plugin-dir ./my-plugin
```

### 마이그레이션 시 변경 사항

| 독립 실행형 (`.claude/`)     | 플러그인                        |
| :---------------------- | :-------------------------- |
| 한 프로젝트에서만 사용 가능         | 마켓플레이스를 통해 공유 가능            |
| `.claude/commands/`의 파일 | `plugin-name/commands/`의 파일 |
| `settings.json`의 훅      | `hooks/hooks.json`의 훅       |
| 공유하려면 수동으로 복사           | `/plugin install`로 설치       |

## 다음 단계

### 플러그인 사용자의 경우

* **플러그인 발견 및 설치**: 마켓플레이스를 검색하고 플러그인을 설치
* **팀 마켓플레이스 구성**: 팀을 위한 저장소 수준 플러그인을 설정

### 플러그인 개발자의 경우

* **마켓플레이스 만들기 및 배포**: 플러그인을 패키징하고 공유
* **플러그인 참조**: 완전한 기술 사양
* 특정 플러그인 구성 요소:
  * **슬래시 명령어**: 명령어 개발 세부 사항
  * **서브에이전트**: 에이전트 구성 및 기능
  * **에이전트 스킬**: Claude의 기능 확장
  * **훅**: 이벤트 처리 및 자동화
  * **MCP**: 외부 도구 통합
