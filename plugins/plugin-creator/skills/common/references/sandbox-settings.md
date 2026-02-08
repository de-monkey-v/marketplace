# Claude Code Sandbox 설정

> 원본: https://code.claude.com/docs/ko/settings#sandbox-설정

샌드박싱은 bash 명령을 파일 시스템 및 네트워크에서 격리합니다.

## Sandbox 설정 키

| 키 | 설명 | 예제 |
|----|------|------|
| `enabled` | bash 샌드박싱 활성화 (macOS, Linux, WSL2) | `true` |
| `autoAllowBashIfSandboxed` | 샌드박싱될 때 bash 명령 자동 승인 (기본: true) | `true` |
| `excludedCommands` | 샌드박스 외부에서 실행해야 하는 명령 | `["git", "docker"]` |
| `allowUnsandboxedCommands` | `dangerouslyDisableSandbox` 매개변수 허용 (기본: true) | `false` |
| `network.allowUnixSockets` | 액세스 가능한 Unix 소켓 경로 | `["~/.ssh/agent-socket"]` |
| `network.allowLocalBinding` | localhost 포트 바인딩 허용 (macOS만, 기본: false) | `true` |
| `network.httpProxyPort` | HTTP 프록시 포트 (자체 프록시 사용 시) | `8080` |
| `network.socksProxyPort` | SOCKS5 프록시 포트 (자체 프록시 사용 시) | `8081` |
| `enableWeakerNestedSandbox` | 권한 없는 Docker 환경에서 약한 샌드박스 활성화 (Linux/WSL2) | `true` |

## 구성 예제

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "excludedCommands": ["docker"],
    "network": {
      "allowUnixSockets": [
        "/var/run/docker.sock"
      ],
      "allowLocalBinding": true
    }
  },
  "permissions": {
    "deny": [
      "Read(.envrc)",
      "Read(~/.aws/**)"
    ]
  }
}
```

## 파일 시스템 및 네트워크 제한

파일 시스템/네트워크 제한은 sandbox 설정이 아닌 표준 권한 규칙 사용:

- `Read` 거부 규칙: 특정 파일/디렉토리 읽기 차단
- `Edit` 허용 규칙: 작업 디렉토리 외부 쓰기 허용
- `Edit` 거부 규칙: 특정 경로 쓰기 차단
- `WebFetch` 허용/거부 규칙: 네트워크 도메인 접근 제어
