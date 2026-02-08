#!/usr/bin/env python3
"""
작업 요약 및 다음 workflow 제안 생성기

Claude Code Stop 훅에서 transcript를 분석하여:
1. 작업 요약 (사용한 도구, 수정한 파일, 실행한 명령어)
2. 다음 workflow 제안 (휴리스틱 기반)

사용법:
    from summarizer import extract_session_summary, build_summary_message, suggest_next_workflows
"""
from __future__ import annotations
import json
import os
from typing import Optional
from collections import Counter


def _process_tool_use(
    tool_name: str,
    tool_input: dict,
    summary: dict,
    seen_tools: set,
    seen_modified: set,
    seen_read: set
) -> None:
    """도구 사용 정보를 summary에 기록하는 헬퍼 함수"""
    summary['tool_counts'][tool_name] += 1
    summary['total_tool_calls'] += 1
    if tool_name not in seen_tools:
        summary['tools_used'].append(tool_name)
        seen_tools.add(tool_name)

    # Bash 명령어 추출
    if tool_name == 'Bash':
        cmd = tool_input.get('command')
        if cmd:
            # 간단하게 첫 100자만
            cmd_short = cmd[:100] + '...' if len(cmd) > 100 else cmd
            summary['commands_executed'].append(cmd_short)

    # 수정된 파일 추출 (Write, Edit)
    elif tool_name in ('Write', 'Edit'):
        file_path = tool_input.get('file_path')
        if file_path and file_path not in seen_modified:
            summary['files_modified'].append(file_path)
            seen_modified.add(file_path)

    # 읽은 파일 추출 (Read)
    elif tool_name == 'Read':
        file_path = tool_input.get('file_path')
        if file_path and file_path not in seen_read:
            summary['files_read'].append(file_path)
            seen_read.add(file_path)


def extract_session_summary(transcript_path: str) -> dict:
    """
    Transcript JSONL 파일에서 세션 작업 요약 정보 추출

    Args:
        transcript_path: transcript 파일 절대 경로

    Returns:
        {
            'user_request': '마지막 사용자 요청',
            'tools_used': ['Bash', 'Write', 'Read'],
            'tool_counts': {'Bash': 5, 'Write': 3, ...},
            'total_tool_calls': 15,
            'files_modified': ['/path/to/file1', '/path/to/file2'],
            'files_read': ['/path/to/file3'],
            'commands_executed': ['npm install', 'npm run build'],
            'errors_encountered': ['Error: ...'],
        }
    """
    summary = {
        'user_request': None,
        'tools_used': [],
        'tool_counts': Counter(),
        'total_tool_calls': 0,
        'files_modified': [],
        'files_read': [],
        'commands_executed': [],
        'errors_encountered': [],
    }

    if not transcript_path or not os.path.exists(transcript_path):
        return summary

    try:
        seen_tools = set()
        seen_modified = set()
        seen_read = set()

        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    obj = json.loads(line)
                    obj_type = obj.get('type')

                    # 사용자 요청 추출 (마지막 것)
                    if obj_type == 'user':
                        msg = obj.get('message', {})
                        content = msg.get('content') if isinstance(msg, dict) else None
                        if isinstance(content, str):
                            text = content.strip()
                            # 시스템 메시지 제외
                            if text and not text.startswith('<') and not text.startswith('# /'):
                                # ❯ 기호 뒤 사용자 입력 추출
                                if '❯' in text:
                                    after_prompt = text.split('❯', 1)[1]
                                    user_input = after_prompt.split('\n')[0].strip()
                                    if user_input:
                                        text = user_input
                                summary['user_request'] = text

                    # 도구 사용 추적 - 새로운 transcript 형식 지원
                    # transcript에서 tool_use는 message.content 배열 안에 있음
                    elif obj_type == 'tool_use':
                        # 새 형식: message.content[].type == 'tool_use'
                        msg = obj.get('message', {})
                        content = msg.get('content', [])
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and item.get('type') == 'tool_use':
                                    tool_name = item.get('name')
                                    tool_input = item.get('input', {})
                                    if tool_name:
                                        _process_tool_use(
                                            tool_name, tool_input, summary,
                                            seen_tools, seen_modified, seen_read
                                        )

                    # assistant 메시지 안의 tool_use도 처리
                    elif obj_type == 'assistant':
                        msg = obj.get('message', {})
                        content = msg.get('content', [])
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and item.get('type') == 'tool_use':
                                    tool_name = item.get('name')
                                    tool_input = item.get('input', {})
                                    if tool_name:
                                        _process_tool_use(
                                            tool_name, tool_input, summary,
                                            seen_tools, seen_modified, seen_read
                                        )

                    # 에러 추적
                    elif obj_type == 'tool_result':
                        msg = obj.get('message', {})
                        content = msg.get('content', [])
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and item.get('is_error'):
                                    error = str(item.get('content', ''))[:200]
                                    if error:
                                        summary['errors_encountered'].append(error)

                except json.JSONDecodeError:
                    continue

        # Counter를 일반 dict로 변환
        summary['tool_counts'] = dict(summary['tool_counts'])
        return summary

    except (FileNotFoundError, PermissionError, IOError):
        return summary


def build_summary_message(summary: dict, max_files: int = 5, max_commands: int = 5) -> str:
    """
    작업 요약 정보를 Slack/Discord용 메시지로 변환

    Args:
        summary: extract_session_summary()의 반환값
        max_files: 표시할 최대 파일 수
        max_commands: 표시할 최대 명령어 수

    Returns:
        Markdown 형식의 요약 메시지
    """
    lines = ["📊 *작업 요약*"]

    # 도구 사용 통계
    if summary['tools_used']:
        tool_stats = []
        for tool in summary['tools_used']:
            count = summary['tool_counts'].get(tool, 0)
            tool_stats.append(f"`{tool}`({count})")
        lines.append(f"- *사용한 도구*: {', '.join(tool_stats)}")
        lines.append(f"- *총 도구 호출*: {summary['total_tool_calls']}회")

    # 수정된 파일
    if summary['files_modified']:
        files = summary['files_modified'][:max_files]
        file_names = [os.path.basename(f) for f in files]
        extra = len(summary['files_modified']) - max_files
        file_list = ', '.join(f"`{f}`" for f in file_names)
        if extra > 0:
            file_list += f" 외 {extra}개"
        lines.append(f"- *수정된 파일*: {file_list}")

    # 실행된 명령어 (간략히)
    if summary['commands_executed']:
        cmds = summary['commands_executed'][:max_commands]
        # 명령어의 첫 부분만 추출 (예: npm install -> npm)
        cmd_summary = []
        seen_cmd_types = set()
        for cmd in cmds:
            cmd_type = cmd.split()[0] if cmd.split() else cmd
            if cmd_type not in seen_cmd_types:
                cmd_summary.append(f"`{cmd_type}`")
                seen_cmd_types.add(cmd_type)
        extra = len(summary['commands_executed']) - len(cmd_summary)
        lines.append(f"- *실행한 명령어*: {', '.join(cmd_summary)} ({len(summary['commands_executed'])}개)")

    # 에러가 있었다면
    if summary['errors_encountered']:
        lines.append(f"- *발생한 에러*: {len(summary['errors_encountered'])}건")

    return '\n'.join(lines)


def suggest_next_workflows(summary: dict, available_skills: Optional[list] = None) -> str:
    """
    휴리스틱 기반으로 다음 workflow 제안 생성

    Args:
        summary: extract_session_summary()의 반환값
        available_skills: 프로젝트에서 사용 가능한 skill 목록 (선택)

    Returns:
        Markdown 형식의 제안 목록
    """
    suggestions = []
    tools_used = set(summary.get('tools_used', []))
    commands = ' '.join(summary.get('commands_executed', []))
    files_modified = summary.get('files_modified', [])

    # 파일 수정 관련 제안
    if files_modified:
        # 테스트 파일이 아닌 코드 파일을 수정했으면
        code_files = [f for f in files_modified
                      if not any(x in f for x in ['test', 'spec', '__test__'])]
        if code_files:
            suggestions.append("🧪 테스트 작성 및 실행 (`/dev-toolkit2:verify`)")

        # 많은 파일 수정시 리뷰 제안
        if len(files_modified) > 3:
            suggestions.append("🔍 코드 리뷰 (`/dev-toolkit2:review`)")

    # Git 관련 제안
    if 'git' in commands.lower():
        if 'add' in commands or 'commit' in commands:
            suggestions.append("📤 변경사항 푸시 및 PR 생성 (`/git-utils:commit`)")
        elif 'status' in commands or 'diff' in commands:
            suggestions.append("💾 변경사항 커밋 (`/git-utils:commit`)")

    # Write/Edit 사용시 (파일 생성/수정)
    if 'Write' in tools_used or 'Edit' in tools_used:
        # JS/TS 파일 수정시
        js_files = [f for f in files_modified
                    if f.endswith(('.js', '.ts', '.jsx', '.tsx'))]
        if js_files:
            suggestions.append("📦 린트 및 타입 체크 (`npm run lint`, `npm run typecheck`)")

        # Python 파일 수정시
        py_files = [f for f in files_modified if f.endswith('.py')]
        if py_files:
            suggestions.append("🐍 Python 린트 (`ruff check`, `mypy`)")

    # npm/yarn 명령어 사용시
    if 'npm' in commands or 'yarn' in commands or 'pnpm' in commands:
        if 'install' in commands:
            suggestions.append("🔒 lockfile 커밋 확인")
        if 'build' in commands:
            suggestions.append("🚀 배포 준비 또는 테스트")

    # 아무 제안이 없으면 기본 제안
    if not suggestions:
        suggestions.append("📝 다음 작업 계획 수립")
        suggestions.append("💬 추가 요청사항 입력")

    # 항상 포함되는 일반 제안
    if 'Write' in tools_used or 'Edit' in tools_used:
        if not any('커밋' in s or 'commit' in s.lower() for s in suggestions):
            suggestions.append("💾 변경사항 커밋 (`/git-utils:commit`)")

    lines = ["💡 *다음 단계 제안*"]
    for suggestion in suggestions[:5]:  # 최대 5개
        lines.append(f"  • {suggestion}")

    return '\n'.join(lines)


def generate_stop_summary(event_data: dict) -> tuple[str, str]:
    """
    Stop 이벤트 데이터로부터 요약 메시지와 workflow 제안 생성

    Args:
        event_data: Stop 훅으로 전달된 이벤트 데이터

    Returns:
        (summary_message, workflow_suggestions) 튜플
    """
    transcript_path = event_data.get('transcript_path')

    # transcript_path가 없으면 cwd + session_id로 구성 (폴백)
    if not transcript_path:
        cwd = event_data.get('cwd', '')
        session_id = event_data.get('session_id', '')
        if cwd and session_id:
            project_path = cwd.replace('/', '-')
            if not project_path.startswith('-'):
                project_path = '-' + project_path
            home = os.path.expanduser('~')
            transcript_path = os.path.join(
                home, '.claude', 'projects', project_path, f'{session_id}.jsonl'
            )

    summary = extract_session_summary(transcript_path)
    summary_msg = build_summary_message(summary)
    workflow_msg = suggest_next_workflows(summary)

    return summary_msg, workflow_msg


# CLI로 직접 실행시 테스트
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        # 인자로 transcript 경로 전달
        path = sys.argv[1]
        summary = extract_session_summary(path)
        print(build_summary_message(summary))
        print()
        print(suggest_next_workflows(summary))
    else:
        # stdin에서 JSON 읽기
        try:
            event_data = json.load(sys.stdin)
            summary_msg, workflow_msg = generate_stop_summary(event_data)
            print(summary_msg)
            print()
            print(workflow_msg)
        except json.JSONDecodeError:
            print("Usage: python summarizer.py <transcript_path>", file=sys.stderr)
            print("   or: echo '{...}' | python summarizer.py", file=sys.stderr)
            sys.exit(1)
