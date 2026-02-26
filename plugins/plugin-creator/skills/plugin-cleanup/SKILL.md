---
name: plugin-cleanup
description: Fix ghost plugins that show as "installed" after uninstalling. This skill should be used when the user asks to "플러그인 정리", "고스트 플러그인 제거", "설치 안 된 플러그인이 installed로 나와", "plugin cleanup", "fix ghost plugins", "remove stale plugins", or mentions plugins appearing as installed after uninstall.
user-invocable: true
argument-hint: "[plugin-name (optional)]"
---

# Plugin Cleanup - Ghost Plugin Remover

설치되지 않았거나 uninstall한 플러그인이 여전히 "installed"로 표시되는 문제를 진단하고 수정합니다.

## Problem Analysis

Claude Code의 플러그인 설치 상태는 두 파일에서 관리됩니다:

| 파일 | 역할 | 경로 |
|------|------|------|
| `installed_plugins.json` | 설치된 플러그인 메타데이터 (설치 경로, 버전, 시간) | `~/.claude/plugins/installed_plugins.json` |
| `settings.json` | 활성화된 플러그인 목록 (`enabledPlugins`) | `~/.claude/settings.json` |

**Ghost Plugin 발생 원인:** uninstall 시 `settings.json`의 `enabledPlugins`에서만 제거되고, `installed_plugins.json`과 캐시 디렉토리에는 항목이 남아있어 UI에서 "installed"로 계속 표시됨.

## Execution Steps

### Step 1: Diagnose Ghost Plugins

두 파일을 읽고 비교합니다:

```bash
# 1. installed_plugins.json에서 모든 플러그인 키 추출
cat ~/.claude/plugins/installed_plugins.json | jq -r '.plugins | keys[]'

# 2. settings.json에서 활성화된 플러그인 키 추출
cat ~/.claude/settings.json | jq -r '.enabledPlugins | keys[]'
```

**Ghost plugin 판별 기준:**
- `installed_plugins.json`에 있지만 `settings.json`의 `enabledPlugins`에 **없는** 플러그인
- 이들이 UI에서 잘못 "installed"로 표시되는 플러그인

### Step 2: Show Diagnosis Results

사용자에게 발견된 ghost 플러그인 목록을 보여줍니다:

```
Ghost Plugins Found:
- {plugin-name}@{marketplace} (installed: {date}, cache: {path})
- ...

Properly Installed Plugins:
- {plugin-name}@{marketplace} (enabled: true)
- ...
```

### Step 3: Ask User What to Remove

사용자에게 어떤 ghost 플러그인을 제거할지 물어봅니다. 인자로 특정 플러그인 이름이 전달된 경우 해당 플러그인만 대상으로 합니다.

### Step 4: Execute Cleanup

사용자가 선택한 각 ghost 플러그인에 대해:

**4a. `installed_plugins.json`에서 항목 제거:**

```bash
# jq로 특정 플러그인 키 제거
jq 'del(.plugins["PLUGIN_KEY"])' ~/.claude/plugins/installed_plugins.json > /tmp/installed_plugins_clean.json
cp ~/.claude/plugins/installed_plugins.json ~/.claude/plugins/installed_plugins.json.bak
mv /tmp/installed_plugins_clean.json ~/.claude/plugins/installed_plugins.json
```

**4b. 캐시 디렉토리 제거:**

```bash
# 캐시 경로는 installed_plugins.json의 installPath 필드에서 확인
rm -rf ~/.claude/plugins/cache/{marketplace}/{plugin-name}/{version}
```

**4c. `settings.json`에서 잔여 항목 제거 (있는 경우):**

`enabledPlugins`에 `false`로 남아있는 항목이 있다면 해당 키도 제거합니다.

### Step 5: Verify Cleanup

```bash
# 정리 후 확인
echo "=== Remaining installed plugins ==="
cat ~/.claude/plugins/installed_plugins.json | jq -r '.plugins | keys[]'
echo ""
echo "=== Enabled plugins ==="
cat ~/.claude/settings.json | jq -r '.enabledPlugins | keys[]'
```

정리 완료 후 Claude Code를 재시작하면 ghost 플러그인이 더 이상 표시되지 않습니다.

## Safety Notes

- `installed_plugins.json`을 수정하기 전에 반드시 `.bak` 백업 파일을 생성합니다
- `enabledPlugins`에 `true`로 활성화된 플러그인은 절대 제거하지 않습니다
- 캐시 디렉토리 삭제 전 사용자에게 확인을 받습니다
- 문제 발생 시 백업에서 복원 안내를 제공합니다

## Related Files

| 파일 | 경로 |
|------|------|
| 설치된 플러그인 메타데이터 | `~/.claude/plugins/installed_plugins.json` |
| 활성화 설정 | `~/.claude/settings.json` |
| 플러그인 캐시 | `~/.claude/plugins/cache/` |
| 차단 목록 | `~/.claude/plugins/blocklist.json` |
| 마켓플레이스 정보 | `~/.claude/plugins/known_marketplaces.json` |
