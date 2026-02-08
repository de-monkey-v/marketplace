#!/usr/bin/env python3
from __future__ import annotations
"""
통합 알림 스크립트

Claude Code 훅 이벤트(Stop, Notification, SessionEnd)를 수신하여
설정된 모든 채널로 알림을 전송합니다.

사용법:
  훅에서 자동 호출: stdin으로 이벤트 JSON 수신 → 모든 활성 채널로 전송

환경변수 (쉼표로 구분하여 여러 URL 설정 가능):
  SLACK_WEBHOOK_URL: Slack Incoming Webhook URL
    예: "https://hooks.slack.com/xxx,https://hooks.slack.com/yyy"
  DISCORD_WEBHOOK_URL: Discord Webhook URL
    예: "https://discord.com/api/webhooks/xxx,https://discord.com/api/webhooks/yyy"
  ENABLE_DESKTOP_NOTIFICATION: "true"로 설정하면 데스크톱 알림 활성화
  ENABLE_WORK_SUMMARY: "true"로 설정하면 작업 통계 포함 (기본값: true)
  ENABLE_EXPERIENCE_SUMMARY: "true"로 설정하면 완료 요약 + 사용 가이드 포함 (기본값: true)

새 채널 추가 방법:
  1. send_xxx() 함수 작성
  2. CHANNELS 딕셔너리에 등록
  3. 환경변수 설정하면 자동 활성화
"""
import json
import sys
import os
import re
import urllib.request
import urllib.error
import subprocess
import platform
from datetime import datetime
from typing import Optional, Callable

# 작업 요약 모듈 import
try:
    from summarizer import generate_stop_summary
    SUMMARIZER_AVAILABLE = True
except ImportError:
    SUMMARIZER_AVAILABLE = False

# 경험 요약 모듈 import (완료 요약 + 사용 가이드)
try:
    from experience_extractor import generate_experience_summary
    EXPERIENCE_EXTRACTOR_AVAILABLE = True
except ImportError:
    EXPERIENCE_EXTRACTOR_AVAILABLE = False

# ============================================================
# 환경 정보 수집
# ============================================================

def get_machine_name() -> str:
    """머신 이름 반환 (Tailscale 우선, hostname 폴백)"""
    # Tailscale 시도
    try:
        result = subprocess.run(
            ["tailscale", "status", "--self", "--json"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            dns_name = data.get("Self", {}).get("DNSName", "")
            if dns_name:
                # "name.tail123.ts.net." → "name"
                return dns_name.split(".")[0]
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    except Exception as e:
        print(f"[Machine] Tailscale error: {e}", file=sys.stderr)

    # hostname 폴백
    return platform.node()


def get_tmux_info() -> Optional[str]:
    """tmux 세션:윈도우 정보 반환 (tmux 외부면 None)"""
    if not os.environ.get("TMUX"):
        return None

    try:
        session = subprocess.run(
            ["tmux", "display-message", "-p", "#S"],
            capture_output=True,
            text=True,
            timeout=1
        ).stdout.strip()

        window = subprocess.run(
            ["tmux", "display-message", "-p", "#W"],
            capture_output=True,
            text=True,
            timeout=1
        ).stdout.strip()

        if session and window:
            return f"{session}:{window}"
        return session or None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    except Exception as e:
        print(f"[tmux] Error: {e}", file=sys.stderr)

    return None


# ============================================================
# 상수 정의
# ============================================================

# 알림 구분선 (메시지 시작에 추가)
MESSAGE_SEPARATOR = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 시스템 메시지 패턴 (사용자 요청으로 표시하지 않을 메시지)
SYSTEM_MESSAGE_PATTERNS: list[str] = [
    'This session is being continued',
    'Context compaction',
    'Session resumed',
    '<system-reminder>',
    '<command-name>',
]


def is_system_message(text: str) -> bool:
    """시스템 메시지 여부 판단"""
    if not text:
        return True
    # 기존 필터: XML 태그나 슬래시 명령어
    if text.startswith('<') or text.startswith('/') or text.startswith('# /'):
        return True
    # 새 필터: 특정 패턴으로 시작하는 시스템 메시지
    for pattern in SYSTEM_MESSAGE_PATTERNS:
        if text.startswith(pattern):
            return True
    return False


STOP_REASON_MAP: dict[str, tuple[str, str]] = {
    # stop_reason: (한글 표시, 아이콘)
    "end_turn": ("작업 완료", "✅"),
    "interrupt_turn": ("사용자 중단", "⚠️"),
}


def get_stop_reason_display(stop_reason: str) -> tuple[str, str]:
    """stop_reason을 한글 표시와 아이콘으로 변환"""
    return STOP_REASON_MAP.get(stop_reason, (stop_reason, "❓"))


# ============================================================
# Transcript 파싱
# ============================================================

def get_transcript_path(cwd: str, session_id: str) -> Optional[str]:
    """
    cwd와 session_id로 transcript 파일 경로 구성

    경로 형식: ~/.claude/projects/{project-path}/{session-id}.jsonl
    project-path: cwd의 /를 -로 변환 (예: /home/user/dev → -home-user-dev)
    """
    if not cwd or not session_id:
        return None

    # /home/user/dev/marketplace → -home-user-dev-marketplace
    project_path = cwd.replace("/", "-")
    if project_path.startswith("-"):
        project_path = project_path  # 이미 -로 시작
    else:
        project_path = "-" + project_path

    home = os.path.expanduser("~")
    transcript_path = os.path.join(home, ".claude", "projects", project_path, f"{session_id}.jsonl")

    return transcript_path if os.path.exists(transcript_path) else None


def extract_command_from_content(content: str) -> Optional[str]:
    """<command-name>/명령어</command-name> 패턴에서 커맨드 추출"""
    match = re.search(r'<command-name>(/[^<]+)</command-name>', content)
    return match.group(1) if match else None


def extract_last_user_message(transcript_path: Optional[str], cwd: str, session_id: str, max_length: int = 500) -> Optional[tuple[str, bool]]:
    """
    Claude Code JSONL 파일에서 마지막 사용자 메시지 또는 커맨드 추출

    Args:
        transcript_path: 이벤트에서 직접 제공된 transcript 경로 (우선 사용)
        cwd: 작업 디렉토리 (프로젝트 경로 구성용, 폴백)
        session_id: 세션 ID (폴백)
        max_length: 최대 문자 수 (기본 500자)

    Returns:
        (message, is_command) 튜플 또는 None
        - message: 사용자 메시지 또는 커맨드
        - is_command: True면 커맨드, False면 일반 메시지
    """
    # 직접 제공된 transcript_path 우선 사용, 없으면 cwd/session_id로 폴백
    if not transcript_path or not os.path.exists(transcript_path):
        transcript_path = get_transcript_path(cwd, session_id)
    if not transcript_path:
        print(f"[Transcript] File not found for session: {session_id}", file=sys.stderr)
        return None

    try:
        last_user_text = None
        is_command = False

        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if obj.get('type') == 'user':
                        msg = obj.get('message', {})
                        content = msg.get('content') if isinstance(msg, dict) else None

                        # content가 문자열인 경우 (실제 사용자 입력)
                        if isinstance(content, str):
                            text = content.strip()

                            # 1. 커맨드 감지 (우선)
                            cmd = extract_command_from_content(text)
                            if cmd:
                                last_user_text = cmd
                                is_command = True
                                continue

                            # 2. "❯" 기호 뒤의 사용자 입력 추출
                            # 형식: "\n❯ 안녕\n\n● 안녕하세요..." → "안녕"
                            if '❯' in text:
                                after_prompt = text.split('❯', 1)[1]  # ❯ 이후
                                # 첫 줄만 추출 (● 이전 또는 줄바꿈 이전)
                                user_input = after_prompt.split('\n')[0].strip()
                                if user_input:
                                    text = user_input

                            # 3. 필터링: 시스템 메시지 제외
                            if not is_system_message(text):
                                last_user_text = text
                                is_command = False

                        # content가 배열인 경우 (tool_result) - 무시
                        # elif isinstance(content, list): pass
                except json.JSONDecodeError:
                    continue

        if not last_user_text:
            return None

        # 첫 줄만 추출하고 길이 제한
        first_line = last_user_text.split('\n')[0].strip()
        if len(first_line) > max_length:
            return (first_line[:max_length-3] + "...", is_command)
        return (first_line, is_command)

    except (FileNotFoundError, PermissionError, IOError) as e:
        print(f"[Transcript] Read error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[Transcript] Parse error: {e}", file=sys.stderr)
        return None


def extract_claude_question(transcript_path: Optional[str], cwd: str, session_id: str) -> Optional[dict]:
    """
    transcript에서 마지막 AskUserQuestion tool_use 추출 (미답변 질문만)

    Args:
        transcript_path: 이벤트에서 직접 제공된 transcript 경로 (우선 사용)
        cwd: 작업 디렉토리 (프로젝트 경로 구성용, 폴백)
        session_id: 세션 ID (폴백)

    Returns:
        질문 데이터 딕셔너리 또는 None (이미 답변된 경우 None)
        {
            "questions": [
                {
                    "question": "질문 내용",
                    "header": "헤더",
                    "options": [{"label": "옵션1", "description": "설명1"}, ...]
                },
                ...
            ]
        }
    """
    # 직접 제공된 transcript_path 우선 사용, 없으면 cwd/session_id로 폴백
    if not transcript_path or not os.path.exists(transcript_path):
        transcript_path = get_transcript_path(cwd, session_id)
    if not transcript_path:
        return None

    try:
        last_question = None
        last_question_id = None
        answered_ids: set[str] = set()

        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)

                    # assistant 메시지에서 AskUserQuestion tool_use 찾기
                    if obj.get('type') == 'assistant':
                        msg = obj.get('message', {})
                        content = msg.get('content') if isinstance(msg, dict) else None

                        if isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get('type') == 'tool_use':
                                    if block.get('name') == 'AskUserQuestion':
                                        input_data = block.get('input', {})
                                        if 'questions' in input_data:
                                            last_question = input_data
                                            last_question_id = block.get('id')

                    # user 메시지에서 tool_result 찾기 (답변된 질문)
                    elif obj.get('type') == 'user':
                        msg = obj.get('message', {})
                        content = msg.get('content') if isinstance(msg, dict) else None

                        if isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get('type') == 'tool_result':
                                    tool_use_id = block.get('tool_use_id')
                                    if tool_use_id:
                                        answered_ids.add(tool_use_id)

                except json.JSONDecodeError:
                    continue

        # 마지막 질문이 이미 답변되었으면 None 반환
        if last_question_id and last_question_id in answered_ids:
            print(f"[Transcript] AskUserQuestion {last_question_id} already answered - skipping", file=sys.stderr)
            return None

        return last_question

    except (FileNotFoundError, PermissionError, IOError) as e:
        print(f"[Transcript] Read error (question): {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[Transcript] Parse error (question): {e}", file=sys.stderr)
        return None


def format_question_section(question_data: dict, max_question_len: int = 80, max_options: int = 4) -> str:
    """
    질문과 선택지를 알림용 텍스트로 포맷팅

    Args:
        question_data: extract_claude_question()의 반환값
        max_question_len: 질문 텍스트 최대 길이 (기본 80자)
        max_options: 표시할 최대 선택지 수 (기본 4개)

    Returns:
        포맷팅된 질문 섹션 문자열
    """
    if not question_data or 'questions' not in question_data:
        return ""

    questions = question_data.get('questions', [])
    if not questions:
        return ""

    sections = []

    for q in questions:
        question_text = q.get('question', '')
        options = q.get('options', [])

        # 질문 텍스트 길이 제한
        if len(question_text) > max_question_len:
            question_text = question_text[:max_question_len - 3] + "..."

        lines = [f"*{question_text}*"]

        # 선택지 포맷팅
        for i, opt in enumerate(options[:max_options], 1):
            label = opt.get('label', '')
            description = opt.get('description', '')

            if description:
                lines.append(f"{i}. {label} - {description}")
            else:
                lines.append(f"{i}. {label}")

        # 남은 선택지가 있으면 표시
        remaining = len(options) - max_options
        if remaining > 0:
            lines.append(f"   (외 {remaining}개)")

        sections.append('\n'.join(lines))

    # 여러 질문이 있으면 구분
    content = '\n\n'.join(sections)

    return f"""
---
❓ *Claude의 질문*

{content}
---"""


# ============================================================
# 메시지 빌더 (이벤트 → 텍스트)
# ============================================================

def build_stop_message(event_data: dict) -> str:
    """Stop 이벤트 메시지 생성"""
    cwd = event_data.get("cwd", "unknown")
    session_id = event_data.get("session_id", "unknown")
    stop_reason = event_data.get("stop_reason", "end_turn")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # stop_reason 한글화
    reason_text, icon = get_stop_reason_display(stop_reason)

    # 헤더 결정
    if stop_reason == "end_turn":
        header = f"{icon} *Claude Code 작업 완료*"
    elif stop_reason == "interrupt_turn":
        header = f"{icon} *Claude Code 작업 중단됨*"
    else:
        header = f"{icon} *Claude Code 작업 종료*"

    # 환경 정보 수집
    machine = get_machine_name()
    tmux = get_tmux_info()
    tmux_line = f"\n- *tmux*: `{tmux}`" if tmux else ""

    # 작업 요약 추출 (transcript_path 우선 사용, 없으면 cwd + session_id로 폴백)
    transcript_path = event_data.get("transcript_path")
    result = extract_last_user_message(transcript_path, cwd, session_id)
    if result:
        user_request, is_command = result
        if is_command:
            request_line = f"\n\n---\n🔧 *실행된 커맨드*\n`{user_request}`\n---"
        else:
            request_line = f"\n\n---\n📝 *사용자 요청*\n\"{user_request}\"\n---"
    else:
        request_line = ""

    # 경험 요약 (완료된 작업 + 사용 방법) - ENABLE_EXPERIENCE_SUMMARY 환경변수로 제어, 기본값: true
    enable_experience = os.environ.get("ENABLE_EXPERIENCE_SUMMARY", "true").lower() == "true"
    experience_section = ""

    if enable_experience and EXPERIENCE_EXTRACTOR_AVAILABLE:
        try:
            completion_summary, usage_guide = generate_experience_summary(event_data)
            if completion_summary:
                experience_section += f"\n\n🎯 *완료된 작업*\n{completion_summary}"
            if usage_guide:
                experience_section += f"\n\n🚀 *사용 방법*\n{usage_guide}"
        except Exception as e:
            print(f"[ExperienceExtractor] Error: {e}", file=sys.stderr)

    # 작업 통계 및 다음 workflow 제안 (ENABLE_WORK_SUMMARY 환경변수로 제어, 기본값: true)
    enable_summary = os.environ.get("ENABLE_WORK_SUMMARY", "true").lower() == "true"
    summary_section = ""
    workflow_section = ""

    if enable_summary and SUMMARIZER_AVAILABLE:
        try:
            summary_msg, workflow_msg = generate_stop_summary(event_data)
            # 작업 통계는 너무 길어서 비활성화 (사용한 도구, 총 도구 호출, 수정된 파일, 실행한 명령어)
            # if summary_msg:
            #     summary_section = f"\n\n{summary_msg}"
            if workflow_msg:
                workflow_section = f"\n\n{workflow_msg}"
        except Exception as e:
            print(f"[Summarizer] Error: {e}", file=sys.stderr)

    return f"""{MESSAGE_SEPARATOR}
{header}

- *시간*: {timestamp}
- *머신*: `{machine}`{tmux_line}
- *작업 폴더*: `{cwd}`
- *Session ID*: `{session_id}`
- *상태*: {reason_text}{request_line}{experience_section}{summary_section}{workflow_section}"""


def build_notification_message(event_data: dict) -> str:
    """Notification 이벤트 메시지 생성"""
    cwd = event_data.get("cwd", "unknown")
    session_id = event_data.get("session_id", "unknown")
    message = event_data.get("message", "응답이 필요합니다")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 환경 정보 수집
    machine = get_machine_name()
    tmux = get_tmux_info()
    tmux_line = f"\n- *tmux*: `{tmux}`" if tmux else ""

    # 사용자 요청 추출 (transcript_path 우선 사용)
    transcript_path = event_data.get("transcript_path")
    result = extract_last_user_message(transcript_path, cwd, session_id)
    if result:
        user_request, is_command = result
        if is_command:
            request_line = f"\n\n---\n🔧 *실행된 커맨드*\n`{user_request}`\n---"
        else:
            request_line = f"\n\n---\n📝 *사용자 요청*\n\"{user_request}\"\n---"
    else:
        request_line = ""

    # Claude 질문 추출 (AskUserQuestion tool_use에서)
    question_section = ""
    question_data = extract_claude_question(transcript_path, cwd, session_id)
    if question_data:
        question_section = format_question_section(question_data)

    return f"""{MESSAGE_SEPARATOR}
💬 *Claude가 응답을 기다립니다*

- *시간*: {timestamp}
- *머신*: `{machine}`{tmux_line}
- *작업 폴더*: `{cwd}`
- *Session ID*: `{session_id}`{request_line}{question_section}"""


def build_session_end_message(event_data: dict) -> str:
    """SessionEnd 이벤트 메시지 생성"""
    cwd = event_data.get("cwd", "unknown")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 환경 정보 수집
    machine = get_machine_name()
    tmux = get_tmux_info()
    tmux_line = f"\n- *tmux*: `{tmux}`" if tmux else ""

    return f"""{MESSAGE_SEPARATOR}
🔚 *Claude Code 세션 종료*

- *시간*: {timestamp}
- *머신*: `{machine}`{tmux_line}
- *작업 폴더*: `{cwd}`"""


def build_message(event_data: dict) -> str:
    """이벤트 타입에 따라 적절한 메시지 생성"""
    event_name = event_data.get("hook_event_name", "")

    builders = {
        "Stop": build_stop_message,
        "Notification": build_notification_message,
        "SessionEnd": build_session_end_message,
    }

    builder = builders.get(event_name)
    if builder:
        return builder(event_data)
    return f"📢 Claude Code 이벤트: {event_name}"


# ============================================================
# 채널별 전송 함수
# ============================================================

def send_slack(message: str, webhook_url: str) -> bool:
    """Slack으로 메시지 전송 (mrkdwn 텍스트)"""
    try:
        payload = {"text": message}
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[Slack] Error: {e}", file=sys.stderr)
        return False


def send_discord(message: str, webhook_url: str) -> bool:
    """Discord로 메시지 전송"""
    try:
        # Discord embed 색상
        event_colors = {
            "✅": 5763719,   # 초록
            "⚠️": 15548997,  # 빨강
            "💬": 3447003,   # 파랑
            "🔚": 9807270,   # 회색
        }

        # 첫 이모지로 색상 결정
        color = 3447003  # 기본 파랑
        for emoji, c in event_colors.items():
            if emoji in message:
                color = c
                break

        # 첫 줄을 제목으로
        lines = message.strip().split('\n')
        title = lines[0] if lines else "Claude Code"
        description = '\n'.join(lines[1:]) if len(lines) > 1 else ""

        payload = {
            "embeds": [{
                "title": title,
                "description": description,
                "color": color
            }]
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 204  # Discord returns 204
    except Exception as e:
        print(f"[Discord] Error: {e}", file=sys.stderr)
        return False


def _escape_powershell(text: str) -> str:
    """PowerShell 문자열 이스케이프"""
    # 백틱(`)으로 특수문자 이스케이프
    return text.replace('`', '``').replace('"', '`"').replace("'", "`'").replace('$', '`$')


def _escape_applescript(text: str) -> str:
    """AppleScript 문자열 이스케이프"""
    return text.replace('\\', '\\\\').replace('"', '\\"')


def send_desktop(message: str, _: str = None) -> bool:
    """데스크톱 알림 전송 (Linux/Windows/Mac)"""
    try:
        # 첫 줄을 제목으로
        lines = message.strip().split('\n')
        title = lines[0] if lines else "Claude Code"
        body = '\n'.join(lines[1:]) if len(lines) > 1 else ""

        system = platform.system()

        if system == "Linux":
            # notify-send (libnotify) - 인자로 전달하므로 안전
            subprocess.run(
                ["notify-send", title, body, "-t", "5000"],
                capture_output=True,
                timeout=5
            )
            return True

        elif system == "Windows":
            # PowerShell Toast - 이스케이프 처리
            safe_title = _escape_powershell(title)
            safe_body = _escape_powershell(body)
            ps_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            $template = [Windows.UI.Notifications.ToastTemplateType]::ToastText02
            $xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent($template)
            $text = $xml.GetElementsByTagName("text")
            $text[0].AppendChild($xml.CreateTextNode("{safe_title}")) | Out-Null
            $text[1].AppendChild($xml.CreateTextNode("{safe_body}")) | Out-Null
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Claude Code").Show($toast)
            '''
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                timeout=5
            )
            return True

        elif system == "Darwin":  # macOS - 이스케이프 처리
            safe_title = _escape_applescript(title)
            safe_body = _escape_applescript(body)
            subprocess.run(
                ["osascript", "-e", f'display notification "{safe_body}" with title "{safe_title}"'],
                capture_output=True,
                timeout=5
            )
            return True

        return False
    except Exception as e:
        print(f"[Desktop] Error: {e}", file=sys.stderr)
        return False


# ============================================================
# 채널 레지스트리
# - 새 채널 추가: 여기에 등록하면 자동 활성화
# ============================================================

CHANNELS: dict[str, dict] = {
    "slack": {
        "env_var": "SLACK_WEBHOOK_URL",
        "sender": send_slack,
    },
    "discord": {
        "env_var": "DISCORD_WEBHOOK_URL",
        "sender": send_discord,
    },
    "desktop": {
        "env_var": "ENABLE_DESKTOP_NOTIFICATION",  # "true"로 설정하면 활성화
        "sender": send_desktop,
    },
    # 새 채널 추가 예시:
    # "teams": {
    #     "env_var": "TEAMS_WEBHOOK_URL",
    #     "sender": send_teams,
    # },
}


# ============================================================
# 메인 로직
# ============================================================

def get_active_channels() -> list[tuple[str, str, Callable]]:
    """환경변수가 설정된 채널 목록 반환 (쉼표로 여러 URL 지원)"""
    active = []
    for name, config in CHANNELS.items():
        env_value = os.environ.get(config["env_var"])
        if env_value:
            # 쉼표로 구분된 여러 URL 지원
            urls = [url.strip() for url in env_value.split(",") if url.strip()]
            for i, url in enumerate(urls):
                # 여러 URL이면 이름에 번호 붙임 (slack, slack_2, slack_3...)
                channel_name = name if i == 0 else f"{name}_{i+1}"
                active.append((channel_name, url, config["sender"]))
    return active


def send_to_all_channels(message: str) -> dict[str, bool]:
    """모든 활성 채널로 메시지 전송"""
    results = {}
    active_channels = get_active_channels()

    if not active_channels:
        print("No channels configured. Set environment variables:", file=sys.stderr)
        for name, config in CHANNELS.items():
            print(f"  - {config['env_var']}", file=sys.stderr)
        return results

    for name, env_value, sender in active_channels:
        results[name] = sender(message, env_value)
        status = "✓" if results[name] else "✗"
        print(f"[{name}] {status}", file=sys.stderr)

    return results


def main():
    # 디버그 정보 출력
    print(f"[notifier.py] PWD: {os.getcwd()}", file=sys.stderr)
    print(f"[notifier.py] hook_event_name from stdin expected", file=sys.stderr)

    # stdin에서 훅 이벤트 수신
    if sys.stdin.isatty():
        print("Usage: Receives hook event JSON from stdin", file=sys.stderr)
        print("\nConfigured channels:", file=sys.stderr)
        for name, config in CHANNELS.items():
            env_value = os.environ.get(config["env_var"])
            status = "✓ active" if env_value else "✗ not set"
            print(f"  {name}: {status} ({config['env_var']})", file=sys.stderr)
        sys.exit(1)

    try:
        event_data = json.load(sys.stdin)
        print(f"[notifier.py] Event: {event_data.get('hook_event_name', 'unknown')}", file=sys.stderr)
        print(f"[notifier.py] Keys: {list(event_data.keys())}", file=sys.stderr)
        if 'transcript_path' in event_data:
            print(f"[notifier.py] transcript_path: {event_data['transcript_path']}", file=sys.stderr)
        else:
            print(f"[notifier.py] transcript_path: NOT PROVIDED", file=sys.stderr)
        message = build_message(event_data)
        results = send_to_all_channels(message)

        # 채널이 설정되지 않은 경우에도 성공으로 처리 (에러 방지)
        if not results:
            print("[notifier.py] No channels configured - skipping silently", file=sys.stderr)
            print(json.dumps({"ok": True}))  # Stop hook 스키마 충족
            sys.exit(0)  # 에러 없이 종료

        # 하나라도 성공하면 성공으로 처리
        success = any(results.values())
        print(json.dumps({"ok": True}))  # Stop hook 스키마 충족 (알림 실패해도 종료 허용)
        sys.exit(0 if success else 1)

    except json.JSONDecodeError:
        print("Invalid JSON input", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
