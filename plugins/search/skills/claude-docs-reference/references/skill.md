# Skills (스킬)

## 검색 키워드
`skill`, `스킬`, `SKILL.md`, `description`, `triggers`, `progressive disclosure`, `동적 컨텍스트`, `ultrathink`, `` `!\` \``, `백틱`, `전처리`, `shell command`, `동적 주입`, `컨텍스트 주입`

---

## [Extend Claude with skills](https://code.claude.com/docs/en/skills)

**포함 주제**: 스킬 개념, 유형, SKILL.md 구조, 발견 메커니즘

### 스킬의 개념
- 지침, 스크립트, 리소스가 조직된 폴더
- 에이전트가 특정 작업에서 더 잘 수행하도록 **동적으로 발견하고 로드**
- 사용자의 전문성을 구성 가능한 리소스로 패킹하여 Claude와 공유

### 스킬의 두 가지 유형
| 유형 | 설명 | 실행 방식 |
|------|------|----------|
| **Reference Content** | 현재 작업에 적용되는 지식 제공 | inline 실행, 대화 컨텍스트와 함께 |
| **Task Content** | 배포, 커밋, 코드 생성 등 단계별 지침 | 작업 수행 가이드 |

### 스킬 위치
| 범위 | 위치 |
|------|------|
| 프로젝트 | `.claude/skills/` |
| 전역 | `~/.claude/skills/` |
| 플러그인 | `plugins/{name}/skills/` |

### 활성화 방식
1. **자동**: description 기반 키워드 매칭
2. **수동**: `/skill-name` 명령어
3. **에이전트 주입**: 에이전트의 `skills:` 필드

---

## [Agent Skills 엔지니어링 블로그](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

**포함 주제**: 설계 철학, Progressive Disclosure, 모범 사례

### Progressive Disclosure 원칙
- Claude는 **필요할 때만** 정보를 로드
- 컨텍스트 윈도우에 전체 내용을 읽지 않음
- Skills를 확장 가능하고 유연하게 만드는 핵심 설계

### 모범 사례
1. **평가로 시작**: 특정 갭을 식별
2. **능력 부족 파악**: 대표적 작업에서 에이전트의 단점 확인
3. **증분식 구축**: 단점을 해결하기 위해 Skills 점진적 추가

---

## [Plugins Reference - Skills 섹션](https://code.claude.com/docs/en/plugins-reference)

**포함 주제**: SKILL.md 명세, 프론트매터 필드, 디렉토리 구조

### SKILL.md 필수 구조
```yaml
---
name: my-skill-name
description: Clear description of what this skill does and when to use it
---

## Overview
[메인 내용]
```

### 프론트매터 필드
| 필드 | 필수 | 제약 |
|------|------|------|
| `name` | O | 최대 64자, 소문자/숫자/하이픈만 |
| `description` | O | 최대 1024자, 비어있으면 안됨 |

### 선택적 제어 필드
| 필드 | 설명 |
|------|------|
| `disable-model-invocation: true` | 사용자만 스킬 호출 가능 (부작용 있는 워크플로우용) |
| `user-invocable: false` | Claude만 호출 가능 (백그라운드 지식용) |

### 스킬 디렉토리 구조
```
skill-name/
├── SKILL.md          # 필수 (YAML 프론트매터 포함)
├── scripts/          # 실행 가능한 코드
├── references/       # 상세 문서
└── assets/           # 출력에 사용되는 파일
```

### 중요 가이드라인
- SKILL.md 본문은 **500줄 이하**로 유지
- 상세한 참고 자료는 별도 파일로 분리 (progressive disclosure)
- name과 description을 명확하고 포괄적으로 작성

---

## 고급 패턴

### 동적 컨텍스트 주입 (`!\` 명령어)

\`!\` 백틱 구문은 스킬이 Claude에게 전송되기 **전에** 셸 명령을 실행합니다.

\```markdown
## Pull request context
- PR diff: !\`gh pr diff\`
- PR comments: !\`gh pr view --comments\`
- Changed files: !\`gh pr diff --name-only\`

## Your task
Summarize this pull request...
```

**작동 방식:**
1. 각 `!\`명령이 **즉시 실행** (Claude가 보기 전)
2. 출력 결과가 자리 표시자를 **대체**
3. Claude는 실제 데이터가 포함된 **완전히 렌더링된 프롬프트**만 수신

**핵심**: 이것은 **전처리 과정**이며, Claude가 실행하는 작업이 아님

### ultrathink 키워드

스킬 콘텐츠에 \`ultrathink` 단어를 포함하면 해당 기술에 대한 **심층적 사고(extended thinking)**가 활성화됩니다.
