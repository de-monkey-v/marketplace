# Plugin Marketplaces (플러그인 마켓플레이스)

## 검색 키워드
`marketplace`, `마켓플레이스`, `marketplace.json`, `플러그인 설치`, `디스커버`, `자동 업데이트`

---

## [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)

**포함 주제**: 마켓플레이스 개념, marketplace.json 구조, 배포 및 관리

### 마켓플레이스란?
- 플러그인을 **일관되게 배포하고 관리**할 수 있는 카탈로그
- 중앙집중식 발견, 버전 추적, 자동 업데이트 지원
- git 저장소, GitHub, 로컬 경로 등 다양한 소스 지원

### marketplace.json 형식
저장소 루트의 `.claude-plugin/marketplace.json`에 정의:

```json
{
  "name": "Your Marketplace Name",
  "owner": "your-org",
  "plugins": [
    {
      "name": "plugin-name",
      "source": "github.com/your-org/plugin-repo"
    }
  ]
}
```

### 필수 필드
| 필드 | 설명 |
|------|------|
| `name` | 마켓플레이스 이름 |
| `owner` | 소유자/조직 |
| `plugins` | 플러그인 목록 (name, source) |

### 배포
- GitHub, GitLab 등에 저장소 푸시
- 유효한 marketplace.json 포함 시 **24시간 이내 자동 발견**

---

## [Discover and install prebuilt plugins](https://code.claude.com/docs/en/discover-plugins)

**포함 주제**: 디스커버 탭, 공식 마켓플레이스, 설치 범위

### 디스커버 탭 인터페이스
`/plugin` 명령어로 4개 탭 접근:

| 탭 | 설명 |
|-----|------|
| Discover | 마켓플레이스 플러그인 검색 |
| Installed | 설치된 플러그인 관리 |
| Marketplaces | 등록된 마켓플레이스 목록 |
| Errors | 에러 확인 |

- Tab 키로 탭 간 이동

### 공식 마켓플레이스
- **claude-plugins-official**: Anthropic 관리
- Claude Code 시작 시 **자동으로 사용 가능**
- 포함 내용:
  - 코드 인텔리전스 플러그인 (LSP 지원)
  - GitHub/Slack 등 외부 통합
  - 개발 워크플로우 도구

### 설치 범위
| 범위 | 설명 |
|------|------|
| User | 사용자 전역 (기본) |
| Project | 프로젝트 범위 |
| Local | 로컬 범위 |

### 보안 주의
- **신뢰할 수 있는 플러그인만 설치**
- Anthropic은 MCP 서버, 파일 등 **검증하지 않음**

---

## 마켓플레이스 명령어

| 작업 | 명령어 |
|------|--------|
| 마켓플레이스 추가 | `/plugin marketplace add owner/repo` |
| 마켓플레이스 목록 | `/plugin marketplace list` |
| 마켓플레이스 갱신 | `/plugin marketplace update <번호>` |
| 마켓플레이스 제거 | `/plugin marketplace remove <번호>` |

## 플러그인 설치 명령어

| 작업 | 명령어 |
|------|--------|
| 기본 설치 (User) | `/plugin install {name}@{marketplace}` |
| 프로젝트 범위 | `/plugin install {name}@{org} --scope project` |
| 로컬 범위 | `/plugin install {name}@{org} --scope local` |
| 제거 | `/plugin uninstall {name}` |
| 활성화 | `/plugin enable {name}` |
| 비활성화 | `/plugin disable {name}` |
