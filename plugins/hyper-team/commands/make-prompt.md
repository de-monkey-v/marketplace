---
name: make-prompt
description: Analyze what you want to build, research the tech stack, create a detailed todo spec, and generate a copy-paste-ready team prompt for a new Claude Code session.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, AskUserQuestion
---

# /hyper-team:make-prompt - Team Prompt Generator

Generate a structured, copy-paste-ready team prompt from your requirements.

**Arguments:** `$ARGUMENTS`

---

## Phase 1: Gather Requirements

<instructions>
If `$ARGUMENTS` is empty or vague, ask the user what they want to build:

```
AskUserQuestion:
- question: "What do you want to build? Describe the feature or task."
- header: "Task"
- options:
  - label: "New feature"
    description: "Build something new from scratch"
  - label: "Bug fix / improvement"
    description: "Fix or improve existing functionality"
  - label: "Refactoring"
    description: "Restructure code without changing behavior"
```

Then ask for more details using AskUserQuestion if needed.

If `$ARGUMENTS` is provided, proceed directly to Phase 2 using it as the task description.
</instructions>

---

## Phase 2: Project Analysis

<instructions>
Analyze the current project to understand the tech stack, architecture, and conventions.

Perform these steps in parallel:
</instructions>

### Step 1: Discover project structure

```
Glob: **/{package.json,requirements.txt,Cargo.toml,go.mod,pom.xml,build.gradle,Gemfile,pyproject.toml,composer.json}
```

```
Glob: **/{tsconfig.json,next.config.*,vite.config.*,webpack.config.*,nuxt.config.*,.env.example}
```

### Step 2: Read key config files

Read the discovered config files to identify:
- Language and runtime version
- Framework and its version
- Key dependencies
- Build tools and scripts
- Environment variables needed

### Step 3: Analyze relevant source code

```
Glob: src/**/*.{ts,tsx,js,jsx,py,go,rs,java}
```

Read relevant files that relate to the user's task to understand:
- Existing code patterns and conventions
- File/folder organization
- API structure
- Database schema (if applicable)

---

## Phase 3: Research

<instructions>
Use WebSearch to look up:

1. Best practices for the identified framework + version
2. Documentation for any new libraries or APIs needed
3. Known issues or gotchas related to the task
4. Community patterns for similar implementations

Think carefully about potential side effects:
</instructions>

<thinking>
Consider and document:
- What existing features could break?
- Are there database migrations needed?
- Will this affect other team members' work?
- Are there API breaking changes?
- Performance implications?
- Security concerns?
</thinking>

---

## Phase 4: Create Todo Document

### Step 1: Determine next number

```
Bash: ls .hyper-team/todos/ 2>/dev/null | sort -n | tail -1 | grep -oP '^\d+' || echo "000"
```

Increment the number by 1 and zero-pad to 3 digits (e.g., 001, 002, 003).

### Step 2: Create the directory

```
Bash: mkdir -p .hyper-team/todos
```

### Step 3: Write the todo document

<instructions>
Write the file to `.hyper-team/todos/NNN-subject.md` where:
- NNN = zero-padded number
- subject = kebab-case short description (e.g., `001-user-auth`, `002-dashboard-chart`)

The document should follow this XML-structured format:
</instructions>

```markdown
# NNN: Subject Title

<task>
Brief description of what needs to be built.
</task>

<context>
## Tech Stack
- Language: {language} {version}
- Framework: {framework} {version}
- Key Dependencies: {list}
- Build Tool: {tool}

## Current Architecture
{Brief description of relevant parts of the codebase}

## Relevant Files
- `path/to/file.ts` - {description}
- `path/to/other.ts` - {description}
</context>

<requirements>
## Functional Requirements
1. {requirement 1}
2. {requirement 2}
3. ...

## Non-Functional Requirements
- Performance: {expectations}
- Security: {considerations}
- Testing: {coverage expectations}
</requirements>

<implementation_plan>
## Approach
{High-level approach description}

## Steps
1. {Step 1 - what to do and where}
2. {Step 2}
3. ...

## Files to Create/Modify
- CREATE: `path/to/new-file.ts` - {purpose}
- MODIFY: `path/to/existing.ts` - {what to change}
</implementation_plan>

<side_effects>
## Potential Risks
- {Risk 1 and mitigation}
- {Risk 2 and mitigation}

## Dependencies
- {Any new dependencies to install}
</side_effects>

<acceptance_criteria>
- [ ] {Criterion 1}
- [ ] {Criterion 2}
- [ ] All tests pass
- [ ] No regressions in existing features
</acceptance_criteria>
```

---

## Phase 5: Generate Team Prompt

<instructions>
Generate a prompt that starts with "Create a team." and is designed for copy-paste into a new Claude Code session.

The prompt should:
1. Start with "Create a team."
2. Define teammate roles based on the task complexity
3. Reference the todo file for detailed specs
4. Include clear instructions for each teammate
5. Apply XML tags for structure
6. Use chain-of-thought where needed
7. Include verification steps for build, run, and browser testing

팀 구성 전략을 결정하라:

<team_strategy>
### 판단 기준
- 같은 작업을 여러 곳에 반복하는가? → **Uniform Workers** 패턴 사용
- 서로 다른 종류의 작업인가? → **Specialized Workers** 패턴 사용
- 혼합인가? → 두 패턴을 조합

### Uniform Workers 패턴
동일한 작업을 여러 파일/모듈에 적용할 때:
- **coordinator** 1명: 공통 규칙 정의, 공유 유틸/컴포넌트 생성, 최종 일관성 검증
- **worker-N** 여러 명: 각자 할당된 파일/모듈에 동일한 패턴으로 작업
- 각 worker에게 담당 파일 목록을 명확히 지정
- coordinator가 먼저 규칙과 공통 코드를 만든 후, worker들이 병렬 작업

예시: 5개 페이지에 i18n 적용
- coordinator: 번역 키 규칙 정의, 공통 유틸 생성
- worker-1: pages/home, pages/about 담당
- worker-2: pages/dashboard, pages/settings 담당
- worker-3: pages/profile 담당 + 통합 테스트

### Specialized Workers 패턴
서로 다른 종류의 작업일 때:
- 역할별 전문 worker (예: backend, frontend, tester)
- 각 worker에게 담당 디렉토리/파일 소유권을 명확히 분리
- 의존관계가 있으면 task dependency 설정

예시: 사용자 인증 기능 구현
- backend: API 엔드포인트, 미들웨어
- frontend: 로그인 UI, 상태 관리
- tester: 단위/통합 테스트 작성
</team_strategy>

Structure the prompt like this:
</instructions>

````markdown
Create a team. Read the task specification at `.hyper-team/todos/NNN-subject.md` and implement it.

<team_structure>
Spawn {N} teammates:
- **{role-1}**: {responsibility description}
- **{role-2}**: {responsibility description}
{...additional roles as needed}
</team_structure>

<instructions>
1. Each teammate should first read `.hyper-team/todos/NNN-subject.md` to understand the full requirements.
2. {Role-1}: {specific tasks and files to work on}
3. {Role-2}: {specific tasks and files to work on}
4. All teammates must run tests after their changes.
</instructions>

<constraints>
- Do not modify files outside the scope defined in the spec.
- Follow existing code conventions and patterns.
- Write tests for all new functionality.
- Coordinate through the shared task list to avoid file conflicts.
</constraints>

<verification>
모든 구현이 완료된 후, 반드시 다음 검증을 수행하라:

## 1단계: 파일 재확인
- 수정한 모든 파일을 다시 Read하여 의도한 변경이 정확히 반영되었는지 확인
- 빠뜨린 부분이나 실수가 없는지 점검

## 2단계: 빌드 검증
- 프로젝트를 빌드하여 에러가 없는지 확인
  ```
  {빌드 커맨드: npm run build / cargo build / go build 등}
  ```

## 3단계: 서버 실행 및 브라우저 테스트
- 개발 서버를 실행하고 실제로 접속하여 동작을 확인
  ```
  {실행 커맨드: npm run dev / python manage.py runserver 등}
  ```
- Playwright 브라우저 도구를 사용하여:
  - `browser_navigate`로 해당 페이지에 접속
  - `browser_snapshot`으로 페이지 상태 캡처
  - `browser_click`으로 버튼/링크 클릭하여 동작 확인
  - `browser_fill`로 폼 입력 테스트
  - 에러가 있으면 수정 후 다시 확인

## 4단계: 테스트 실행
- 전체 테스트 스위트를 실행하여 모든 테스트가 통과하는지 확인
  ```
  {테스트 커맨드: npm test / pytest / go test 등}
  ```
- 실패하는 테스트가 있으면 수정하고 재실행

## 5단계: 최종 확인
- 검증을 모두 통과한 후에만 todo 파일을 완료로 변경:
  ```
  mv .hyper-team/todos/NNN-subject.md .hyper-team/todos/NNN-subject-complete.md
  ```
</verification>
````

---

## Phase 6: Present to User

<instructions>
Display the generated prompt using the template below. The `==== copy ====` and `==== end ====` markers make it easy for the user to identify the exact text to copy.

Output the following, replacing the placeholders with actual content:
</instructions>

```markdown
## Your Team Prompt is Ready

The task spec has been saved to: `.hyper-team/todos/NNN-subject.md`

아래 템플릿을 복사하세요.
==== copy ====
{생성된 팀 프롬프트 전체 내용}
==== end ====

### How to Use
1. **Copy** 위의 `==== copy ====` ~ `==== end ====` 사이의 내용을 복사
2. **Open a new session** (recommended) or run `/clear` in the current session
3. **Paste** the prompt and press Enter
4. Claude will create a team and start working on the task

> **Tip**: Opening a new terminal session is recommended so this session's context doesn't interfere with the team's work. You can run `claude` in a new terminal window.

### After Completion
Once the team finishes, the todo file will be automatically renamed to:
`.hyper-team/todos/NNN-subject-complete.md`

You can verify the implementation with:
`/hyper-team:verify NNN`
```
