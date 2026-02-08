#!/usr/bin/env python3
"""
작업 완료 요약 및 사용자 경험 가이드 추출기

Claude Code Stop 훅에서 Claude의 응답을 분석하여:
1. 완료 요약: "어떤 기능이 추가/수정되었는지" 추출
2. 사용 가이드: "어떻게 테스트/사용해볼 수 있는지" 추출

사용법:
    from experience_extractor import generate_experience_summary

    # Stop 이벤트에서 호출
    completion_summary, usage_guide = generate_experience_summary(event_data)
"""
from __future__ import annotations
import json
import os
import re
from typing import Optional


def _get_transcript_path(event_data: dict) -> Optional[str]:
    """이벤트 데이터에서 transcript 경로 구성"""
    transcript_path = event_data.get('transcript_path')

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

    return transcript_path if transcript_path and os.path.exists(transcript_path) else None


def _extract_assistant_texts(transcript_path: str) -> list[str]:
    """
    Transcript에서 모든 assistant text 응답 추출 (역순 아님, 원래 순서)

    Returns:
        assistant text 응답 목록
    """
    texts = []

    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if obj.get('type') == 'assistant':
                        content = obj.get('message', {}).get('content', [])
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and item.get('type') == 'text':
                                    text = item.get('text', '')
                                    if text:
                                        texts.append(text)
                except json.JSONDecodeError:
                    continue
    except (FileNotFoundError, PermissionError, IOError):
        pass

    return texts


def _find_completion_section(texts: list[str]) -> Optional[str]:
    """
    마지막부터 '완료' 관련 섹션 포함하는 텍스트 찾기

    완료 마커 패턴:
    - ## 완료 요약
    - ## 완료
    - ## Phase 7:  (보통 마지막 단계)
    - ## 구현 완료
    - ## 작업 완료
    """
    completion_markers = [
        '## 완료 요약',
        '## 완료',
        '## 구현 완료',
        '## 작업 완료',
        '## Phase 7',  # 계획 마지막 단계
        '작업이 완료되었습니다',
        '구현이 완료되었습니다',
    ]

    # 마지막부터 탐색
    for text in reversed(texts):
        for marker in completion_markers:
            if marker in text:
                return text

    return None


def _parse_completion_summary(text: str) -> Optional[str]:
    """
    완료 텍스트에서 주요 내용 추출

    추출 대상:
    - 기능/변경사항 설명
    - 생성/수정된 파일 목록
    - 주요 구현 내용

    Returns:
        요약된 완료 내용 (최대 5줄)
    """
    if not text:
        return None

    lines = []

    # 1. ## 완료 섹션 내용 추출
    completion_patterns = [
        r'##\s*완료.*?\n((?:[-*]\s*.+\n?)+)',  # ## 완료 아래 불릿 리스트
        r'##\s*구현\s*완료.*?\n((?:[-*]\s*.+\n?)+)',
        r'##\s*작업\s*완료.*?\n((?:[-*]\s*.+\n?)+)',
    ]

    for pattern in completion_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            bullet_content = match.group(1)
            for line in bullet_content.strip().split('\n'):
                line = line.strip()
                if line.startswith(('-', '*')):
                    # 불릿 제거하고 내용만
                    content = re.sub(r'^[-*]\s*', '', line).strip()
                    if content and len(content) > 5:
                        lines.append(f"• {content}")
            break

    # 2. 생성/수정된 파일 섹션 추출
    file_patterns = [
        r'###?\s*(?:생성|수정|변경)[된\s]*파일.*?\n((?:[-*]\s*`?.+`?\n?)+)',
        r'###?\s*(?:Created|Modified)\s*Files.*?\n((?:[-*]\s*`?.+`?\n?)+)',
    ]

    for pattern in file_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            file_content = match.group(1)
            files = []
            for line in file_content.strip().split('\n'):
                line = line.strip()
                if line.startswith(('-', '*')):
                    # 파일명 추출 (백틱 포함 또는 미포함)
                    content = re.sub(r'^[-*]\s*', '', line).strip()
                    # 백틱 안의 내용 또는 전체 라인
                    file_match = re.search(r'`([^`]+)`', content)
                    if file_match:
                        files.append(file_match.group(1))
                    elif content:
                        files.append(content.split()[0])  # 첫 단어만
            if files:
                # 파일명만 추출하여 간결하게
                file_names = [os.path.basename(f) for f in files[:5]]
                lines.append(f"• 파일: {', '.join(file_names)}")
            break

    # 3. 주요 기능 설명 추출 (첫 문단에서)
    if not lines:
        # "구현", "추가", "생성" 등의 동사로 시작하는 문장 찾기
        action_patterns = [
            r'([가-힣\w\s]+(?:구현|추가|생성|수정|완료)[했습니다되었습니다\.]+)',
            r'((?:Added|Created|Implemented|Modified|Updated)\s+[^.]+\.)',
        ]

        for pattern in action_patterns:
            matches = re.findall(pattern, text)
            for m in matches[:3]:  # 최대 3개
                content = m.strip()
                if len(content) > 10 and len(content) < 100:
                    lines.append(f"• {content}")

    if not lines:
        return None

    return '\n'.join(lines[:5])  # 최대 5줄


def _find_usage_section(texts: list[str]) -> Optional[str]:
    """
    사용법/테스트 방법 포함하는 텍스트 찾기

    사용법 마커:
    - ### 사용법
    - ### 사용 방법
    - ### 테스트
    - ### 테스트 방법
    - ### 설정
    - ### 환경변수
    - ### 실행 방법
    """
    usage_markers = [
        '### 사용법',
        '### 사용 방법',
        '### 테스트 방법',
        '### 테스트',
        '### 설정',
        '### 환경변수',
        '### 실행 방법',
        '### How to use',
        '### How to test',
        '### Usage',
    ]

    # 마지막부터 탐색
    for text in reversed(texts):
        for marker in usage_markers:
            if marker in text:
                return text

    return None


def _parse_usage_guide(text: str) -> Optional[str]:
    """
    사용법 텍스트에서 핵심 가이드 추출

    추출 대상:
    - 코드 블록 (bash, shell 명령어)
    - 순서가 있는 설명 (1., 2., 3.)
    - 불릿 리스트

    Returns:
        사용 가이드 (최대 5줄)
    """
    if not text:
        return None

    lines = []

    # 1. 코드 블록에서 bash/shell 명령어 추출
    code_pattern = r'```(?:bash|shell|sh)?\n([\s\S]*?)```'
    code_matches = re.findall(code_pattern, text)

    for code in code_matches:
        code_lines = code.strip().split('\n')
        for line in code_lines:
            line = line.strip()
            # 주석이나 빈 줄 제외
            if line and not line.startswith('#'):
                lines.append(f"`{line}`")
                if len(lines) >= 3:
                    break
        if len(lines) >= 3:
            break

    # 2. 사용법 섹션 아래 불릿/번호 리스트 추출
    usage_patterns = [
        r'###?\s*(?:사용법|사용\s*방법|테스트|실행\s*방법).*?\n((?:\d+\.\s*.+\n?)+)',
        r'###?\s*(?:사용법|사용\s*방법|테스트|실행\s*방법).*?\n((?:[-*]\s*.+\n?)+)',
    ]

    for pattern in usage_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            list_content = match.group(1)
            for line in list_content.strip().split('\n'):
                line = line.strip()
                if line:
                    # 번호 또는 불릿 제거
                    content = re.sub(r'^(\d+\.|-|\*)\s*', '', line).strip()
                    if content and len(content) > 5:
                        lines.append(content)
                        if len(lines) >= 5:
                            break
            break

    # 3. URL 추출 (localhost, 127.0.0.1 등)
    url_pattern = r'(https?://(?:localhost|127\.0\.0\.1)[:\d]*[^\s\)\"\']*)'
    url_matches = re.findall(url_pattern, text)
    for url in url_matches[:2]:  # 최대 2개
        if url not in '\n'.join(lines):
            lines.append(f"접속: {url}")

    if not lines:
        return None

    # 중복 제거 및 최대 5줄
    seen = set()
    unique_lines = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    return '\n'.join(unique_lines[:5])


def extract_completion_summary(transcript_path: str) -> Optional[str]:
    """
    Claude 응답에서 '완료 요약' 섹션 추출

    Args:
        transcript_path: transcript JSONL 파일 경로

    Returns:
        완료 요약 텍스트 또는 None
    """
    if not transcript_path:
        return None

    texts = _extract_assistant_texts(transcript_path)
    if not texts:
        return None

    completion_text = _find_completion_section(texts)
    if not completion_text:
        return None

    return _parse_completion_summary(completion_text)


def extract_usage_guide(transcript_path: str) -> Optional[str]:
    """
    Claude 응답에서 '사용 방법/테스트 방법' 섹션 추출

    Args:
        transcript_path: transcript JSONL 파일 경로

    Returns:
        사용 가이드 텍스트 또는 None
    """
    if not transcript_path:
        return None

    texts = _extract_assistant_texts(transcript_path)
    if not texts:
        return None

    usage_text = _find_usage_section(texts)
    if not usage_text:
        return None

    return _parse_usage_guide(usage_text)


def generate_experience_summary(event_data: dict) -> tuple[Optional[str], Optional[str]]:
    """
    Stop 이벤트에서 호출할 메인 함수

    Claude 응답에서 완료 요약과 사용 가이드를 추출합니다.

    Args:
        event_data: Stop 훅으로 전달된 이벤트 데이터

    Returns:
        (completion_summary, usage_guide) 튜플
        - completion_summary: "어떤 기능이 추가/수정되었는지"
        - usage_guide: "어떻게 테스트/사용해볼 수 있는지"
    """
    transcript_path = _get_transcript_path(event_data)
    if not transcript_path:
        return None, None

    completion_summary = extract_completion_summary(transcript_path)
    usage_guide = extract_usage_guide(transcript_path)

    return completion_summary, usage_guide


# CLI로 직접 실행시 테스트
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        # 인자로 transcript 경로 전달
        path = sys.argv[1]

        print("=== Completion Summary ===")
        summary = extract_completion_summary(path)
        if summary:
            print(summary)
        else:
            print("(none found)")

        print()
        print("=== Usage Guide ===")
        guide = extract_usage_guide(path)
        if guide:
            print(guide)
        else:
            print("(none found)")
    else:
        print("Usage: python experience_extractor.py <transcript_path>", file=sys.stderr)
        sys.exit(1)
