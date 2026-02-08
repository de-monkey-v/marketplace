# MCP (Model Context Protocol)

## 검색 키워드
`MCP`, `Model Context Protocol`, `mcp.json`, `mcpServers`, `Tool Search`, `리소스`, `.mcpb`, `Desktop Extension`

---

## [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)

**포함 주제**: MCP 개념, 리소스 참조, Tool Search, 토큰 관리

### MCP란?
- 외부 도구, 데이터베이스, API를 Claude Code와 연결하는 **오픈 소스 표준**
- 수백 개의 외부 도구와 데이터 소스에 접근 가능

### 주요 기능

**리소스 참조**
- 파일처럼 `@` 멘션을 사용하여 MCP 서버의 리소스에 접근

**Tool Search**
- 도구가 많을 경우 **동적으로 필요한 도구만 로드**
- 도구 설명이 컨텍스트의 10% 이상일 때 자동 활성화
- 컨텍스트 윈도우 절약

**출력 관리**
- MCP 도구 출력이 10,000 토큰 초과 시 경고 표시
- `MAX_MCP_OUTPUT_TOKENS` 환경변수로 제한 설정 (기본값: 25,000)

### 설정 위치
| 범위 | 위치 |
|------|------|
| 전역 | `~/.claude/mcp.json` |
| 프로젝트 | `.claude/mcp.json` |
| 플러그인 | `plugin.json`의 `mcpServers` |

### MCP 서버 추가 방법
```bash
# CLI 방식
claude mcp add github --scope user

# 설정 파일 직접 편집
~/.claude/mcp.json
```

---

## [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)

**포함 주제**: 코드 실행 패턴, 토큰 효율성, TypeScript 기반 실행

### 혁신적인 접근법
- **기존**: 모델이 직접 MCP 도구를 호출
- **새로운 방식**: MCP 서버를 파일시스템 기반 코드 모듈로 노출, 모델이 TypeScript 코드 작성 및 실행

### 극적인 성능 개선
| 방식 | 토큰 소비 |
|------|----------|
| 기존 방식 | ~150,000 토큰 |
| 코드 실행 패턴 | ~2,000 토큰 |

**98.7% 토큰 감소** → 비용 및 지연시간 단축

### 구현 방식
```
1. MCP 클라이언트가 각 서버를 코드 모듈 세트로 노출
2. 모델이 TypeScript 코드 작성 (해당 모듈 import)
3. 코드를 샌드박싱된 환경에서 실행
4. 결과를 모델에 반환
```

### 보안 고려사항
- 샌드박싱 환경에서 실행
- 리소스 제한 및 모니터링 필요

---

## [Desktop extensions (One-click MCP Installation)](https://www.anthropic.com/engineering/desktop-extensions)

**포함 주제**: .mcpb 파일 형식, 원클릭 설치, Cowork 기능

### Desktop Extension (.mcpb)란?
- 모든 의존성을 포함한 완전한 MCP 서버를 **단일 설치 가능한 패키지**로 번들
- Chrome 확장(.crx)이나 VS Code 확장(.vsix)과 유사

### 설치 프로세스
```
사용자: .mcpb 파일 다운로드 → 더블클릭
자동 구성: Claude가 자동으로 설정 완료 및 자격증명 프롬프트 제공
```

### 개발자 프로세스
```bash
cd my-mcp-server
mcpb init          # manifest.json 대화형 생성
mcpb pack          # my-mcp-server.mcpb 생성
```

### 2026 주요 개선
- **Cowork 기능**: Claude를 디지털 동료로 전환, 터미널 없이 복잡한 다단계 작업 수행
- **데스크톱 통합**: 로컬 파일, 캘린더, 이메일과 원클릭 연결
- **비기술 사용자 접근성**: 직관적 인터페이스로 AI 에이전트 기능 제공

---

## 일반적인 MCP 서버

| 서버 | 용도 |
|------|------|
| filesystem | 파일 시스템 접근 |
| puppeteer | 브라우저 자동화 |
| playwright | 브라우저 테스팅 |
| context7 | 라이브러리 문서 검색 |
| github | GitHub API 연동 |
