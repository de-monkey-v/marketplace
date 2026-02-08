# Claude Code 플러그인 구성

> 원본: https://code.claude.com/docs/ko/settings#플러그인-구성

## 플러그인 설정 예제

```json
{
  "enabledPlugins": {
    "formatter@acme-tools": true,
    "deployer@acme-tools": true,
    "analyzer@security-plugins": false
  },
  "extraKnownMarketplaces": {
    "acme-tools": {
      "source": "github",
      "repo": "acme-corp/claude-plugins"
    }
  }
}
```

## enabledPlugins

활성화된 플러그인 제어. 형식: `"plugin-name@marketplace-name": true/false`

### 범위
- **사용자 설정** (`~/.claude/settings.json`): 개인 플러그인 설정
- **프로젝트 설정** (`.claude/settings.json`): 팀 공유 프로젝트별 플러그인
- **Local 설정** (`.claude/settings.local.json`): 머신별 재정의 (커밋되지 않음)

## extraKnownMarketplaces

저장소에서 사용 가능하게 할 추가 마켓플레이스 정의.

저장소에 포함될 때:
1. 팀 멤버는 폴더 신뢰 시 마켓플레이스 설치 메시지 표시
2. 해당 마켓플레이스에서 플러그인 설치 메시지 표시
3. 원하지 않는 마켓플레이스/플러그인 건너뛰기 가능

### 마켓플레이스 소스 유형
- `github`: GitHub 저장소 (`repo` 사용)
- `git`: 모든 git URL (`url` 사용)
- `directory`: 로컬 파일 시스템 경로 (`path` 사용, 개발 전용)

```json
{
  "extraKnownMarketplaces": {
    "acme-tools": {
      "source": {
        "source": "github",
        "repo": "acme-corp/claude-plugins"
      }
    },
    "security-plugins": {
      "source": {
        "source": "git",
        "url": "https://git.example.com/security/plugins.git"
      }
    }
  }
}
```

## strictKnownMarketplaces (Managed 전용)

사용자가 추가할 수 있는 마켓플레이스 제어. `managed-settings.json`에서만 구성 가능.

### 허용 목록 동작
- `undefined` (기본값): 제한 없음
- 빈 배열 `[]`: 완전 잠금
- 소스 목록: 정확히 일치하는 마켓플레이스만 허용

### 지원되는 소스 유형

**1. GitHub 저장소**
```json
{ "source": "github", "repo": "acme-corp/approved-plugins" }
{ "source": "github", "repo": "acme-corp/security-tools", "ref": "v2.0" }
```

**2. Git 저장소**
```json
{ "source": "git", "url": "https://gitlab.example.com/tools/plugins.git" }
```

**3. URL 기반**
```json
{ "source": "url", "url": "https://plugins.example.com/marketplace.json" }
```

**4. NPM 패키지**
```json
{ "source": "npm", "package": "@acme-corp/claude-plugins" }
```

**5. 파일 경로**
```json
{ "source": "file", "path": "/usr/local/share/claude/acme-marketplace.json" }
```

**6. 디렉토리 경로**
```json
{ "source": "directory", "path": "/usr/local/share/claude/acme-plugins" }
```

## extraKnownMarketplaces vs strictKnownMarketplaces

| 측면 | strictKnownMarketplaces | extraKnownMarketplaces |
|------|------------------------|----------------------|
| **목적** | 조직 정책 적용 | 팀 편의성 |
| **설정 파일** | `managed-settings.json`만 | 모든 설정 파일 |
| **동작** | 허용 목록이 아닌 추가 차단 | 누락된 마켓플레이스 자동 설치 |
| **재정의 가능** | 아니오 (최상위 우선순위) | 예 |
| **사용 사례** | 규정 준수, 보안 제한 | 온보딩, 표준화 |
