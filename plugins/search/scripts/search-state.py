#!/usr/bin/env python3
"""
검색 API 상태 관리 (로드 밸런싱)

Brave/Tavily API를 라운드 로빈 방식으로 번갈아 사용하여
크레딧 소비를 균등하게 분산합니다.

Usage:
    python3 search-state.py next              # 다음 사용할 API 반환
    python3 search-state.py used <api>        # API 사용 기록
    python3 search-state.py unavailable <api> # API 사용 불가 표시
    python3 search-state.py reset             # 상태 초기화
    python3 search-state.py status            # 현재 상태 출력
"""
import json
import sys
from pathlib import Path
from datetime import datetime

STATE_FILE = Path(__file__).parent.parent / ".search-state.json"


def load_state() -> dict:
    """상태 파일 로드"""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {
        "lastUsedApi": "brave",  # 초기값: brave -> 첫 검색은 tavily 사용
        "braveAvailable": True,
        "tavilyAvailable": True,
        "lastUpdated": None,
        "usageCount": {"brave": 0, "tavily": 0}
    }


def save_state(state: dict) -> None:
    """상태 파일 저장"""
    state["lastUpdated"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def get_next_api() -> str:
    """다음에 사용할 API 반환 (라운드 로빈)"""
    state = load_state()

    # 라운드 로빈: 마지막 사용 API의 반대쪽 선택
    if state["lastUsedApi"] == "brave":
        # Tavily 우선, 불가하면 Brave
        if state["tavilyAvailable"]:
            return "tavily"
        elif state["braveAvailable"]:
            return "brave"
    else:
        # Brave 우선, 불가하면 Tavily
        if state["braveAvailable"]:
            return "brave"
        elif state["tavilyAvailable"]:
            return "tavily"

    # 둘 다 불가하면 None 반환
    return "none"


def mark_used(api_name: str) -> None:
    """API 사용 기록"""
    if api_name not in ("brave", "tavily"):
        print(f"Error: Invalid API name '{api_name}'. Use 'brave' or 'tavily'.", file=sys.stderr)
        sys.exit(1)

    state = load_state()
    state["lastUsedApi"] = api_name

    # 사용 횟수 증가
    if "usageCount" not in state:
        state["usageCount"] = {"brave": 0, "tavily": 0}
    state["usageCount"][api_name] = state["usageCount"].get(api_name, 0) + 1

    save_state(state)
    print(f"Marked {api_name} as used")


def mark_unavailable(api_name: str) -> None:
    """API 사용 불가 표시 (크레딧 소진 등)"""
    if api_name not in ("brave", "tavily"):
        print(f"Error: Invalid API name '{api_name}'. Use 'brave' or 'tavily'.", file=sys.stderr)
        sys.exit(1)

    state = load_state()
    state[f"{api_name}Available"] = False
    save_state(state)
    print(f"Marked {api_name} as unavailable")


def reset_state() -> None:
    """상태 초기화"""
    state = {
        "lastUsedApi": "brave",
        "braveAvailable": True,
        "tavilyAvailable": True,
        "lastUpdated": datetime.now().isoformat(),
        "usageCount": {"brave": 0, "tavily": 0}
    }
    save_state(state)
    print("State reset to default")


def show_status() -> None:
    """현재 상태 출력"""
    state = load_state()
    print(json.dumps(state, indent=2, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "next":
        print(get_next_api())
    elif cmd == "used":
        if len(sys.argv) < 3:
            print("Error: API name required. Usage: search-state.py used <brave|tavily>", file=sys.stderr)
            sys.exit(1)
        mark_used(sys.argv[2])
    elif cmd == "unavailable":
        if len(sys.argv) < 3:
            print("Error: API name required. Usage: search-state.py unavailable <brave|tavily>", file=sys.stderr)
            sys.exit(1)
        mark_unavailable(sys.argv[2])
    elif cmd == "reset":
        reset_state()
    elif cmd == "status":
        show_status()
    else:
        print(f"Error: Unknown command '{cmd}'", file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
