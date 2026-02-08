# Plugins (플러그인)

## 검색 키워드
`plugin`, `플러그인`, `plugin.json`, `.claude-plugin`, `skills`, `agents`, `commands`, `hooks`, `mcpServers`

---

## [Create plugins](https://code.claude.com/docs/en/plugins)

**포함 주제**: 플러그인 개념, 구조, 개발, 설치, 공유

### 플러그인이란
- Claude Code를 확장하여 **커스텀 기능을 추가**하는 패키지
- Skills, Agents, Hooks, MCP Servers를 통해 기능 확장
- 프로젝트와 팀 간에 공유 가능하여 일관된 워크플로우 제공

### 플러그인 구조
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json      # 필수: 매니페스트
├── skills/              # 선택: 스킬
├── agents/              # 선택: 에이전트
├── commands/            # 선택: 슬래시 명령어
└── hooks/hooks.json     # 선택: 훅
```

### plugin.json 필수 구조
```json
{
  "name": "my-plugin",
  "description": "Plugin description",
  "version": "1.0.0"
}
```

### Auto-Discovery
- 각 컴포넌트는 기본 디렉토리에서 **자동으로 발견**됨
- 명시적 설정 없이 표준 디렉토리에 배치하면 로드

---

## [Plugins Reference](https://code.claude.com/docs/en/plugins-reference)

**포함 주제**: plugin.json 스키마, 컴포넌트별 상세 설정

### plugin.json 필드
| 필드 | 설명 |
|------|------|
| `name` | 플러그인 이름 |
| `version` | 버전 (semver) |
| `description` | 설명 |
| `keywords` | 검색 키워드 |
| `mcpServers` | MCP 서버 설정 |

### 컴포넌트별 역할
| 컴포넌트 | 역할 | 활성화 방식 |
|----------|------|------------|
| **Skills** | 특정 작업을 위한 지식/가이드 | description 기반 자동 |
| **Agents** | 복잡한 작업 자동화 | Claude가 필요시 선택 |
| **Commands** | `/명령어` 형식 사용자 호출 | 슬래시 입력 |
| **Hooks** | 이벤트 기반 자동화 | 이벤트 트리거 |

### 중요 개발 가이드라인
- **경로 포터빌리티**: hooks와 MCP에서 `${CLAUDE_PLUGIN_ROOT}` 사용
- **컴포넌트 배치**: commands/, agents/, skills/는 `.claude-plugin/` **외부**에 위치
- **스킬 크기**: SKILL.md는 500줄 이하, 복잡한 로직은 스크립트로 위임

---

## [Discover Plugins](https://code.claude.com/docs/en/discover-plugins)

**포함 주제**: 플러그인 발견, 마켓플레이스, 설치, 보안

### 플러그인 발견 방법
- `/plugin` 명령어로 Discover 탭 접근
- 공식 Anthropic 마켓플레이스는 자동 제공

### 마켓플레이스 종류
| 종류 | 예시 |
|------|------|
| 공식 | anthropic의 claude-plugins-official |
| 커뮤니티 | claude-plugins.dev, claudecodemarketplace.com |
| 내부 | 팀 자체 마켓플레이스 |

### 설치 및 신뢰성
- 플러그인 설치 전 **신뢰 여부 확인** 필요
- Anthropic은 플러그인의 MCP 서버, 파일 등을 **검증하지 않음**
- 설치 후 Claude Code 재시작하여 로드

---

## 플러그인 명령어

| 명령어 | 설명 |
|--------|------|
| `/plugin list` | 설치된 플러그인 목록 |
| `/plugin enable <name>` | 활성화 |
| `/plugin disable <name>` | 비활성화 |
| `/plugin install <source>` | 설치 |
| `/plugin uninstall <name>` | 제거 |
