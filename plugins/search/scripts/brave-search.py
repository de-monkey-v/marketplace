#!/usr/bin/env python3
"""Brave Web Search API - 웹 검색
Usage: brave-search.py "query" [options]

Options:
  --count N           결과 수 (1-20, default: 10)
  --offset N          페이지네이션 (0-9, default: 0)
  --country CODE      국가 코드 (US, KR 등)
  --lang CODE         검색 언어 (en, ko 등)
  --freshness PERIOD  기간 필터 (pd/pw/pm/py)
  --safesearch LEVEL  off / moderate / strict (default: moderate)
  --output FILE       결과를 파일로 저장

Examples:
  brave-search.py "React 19 new features"
  brave-search.py "TypeScript tutorial" --count 20
  brave-search.py "AI news" --freshness pw
  brave-search.py "local events" --country US --lang en
"""
import sys
import os
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error

API_KEY = os.environ.get("BRAVE_API_KEY", "")
BASE_URL = "https://api.search.brave.com/res/v1/web/search"


def main():
    parser = argparse.ArgumentParser(
        description="Brave Web Search API - 웹 검색",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("query", help="검색 쿼리")
    parser.add_argument("--count", type=int, default=10,
                        help="결과 수 (1-20, default: 10)")
    parser.add_argument("--offset", type=int, default=0,
                        help="페이지네이션 (0-9, default: 0)")
    parser.add_argument("--country",
                        help="국가 코드 (US, KR 등)")
    parser.add_argument("--lang",
                        help="검색 언어 (en, ko 등)")
    parser.add_argument("--freshness", choices=["pd", "pw", "pm", "py"],
                        help="기간 필터 (pd=day, pw=week, pm=month, py=year)")
    parser.add_argument("--safesearch", choices=["off", "moderate", "strict"],
                        default="moderate", help="안전 검색 수준 (default: moderate)")
    parser.add_argument("--output", "-o", help="결과를 파일로 저장")

    args = parser.parse_args()

    if not API_KEY:
        print("Error: BRAVE_API_KEY 환경변수가 설정되지 않았습니다.")
        print("설정: export BRAVE_API_KEY='your-api-key'")
        print("발급: https://api.search.brave.com/")
        sys.exit(1)

    # Build query parameters
    params = {
        "q": args.query,
        "count": min(max(args.count, 1), 20),
        "offset": min(max(args.offset, 0), 9),
        "safesearch": args.safesearch,
    }

    if args.country:
        params["country"] = args.country
    if args.lang:
        params["search_lang"] = args.lang
    if args.freshness:
        params["freshness"] = args.freshness

    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
    headers = {
        "X-Subscription-Token": API_KEY,
        "Accept": "application/json",
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            result = json.dumps(data, indent=2, ensure_ascii=False)

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(result)
                print(f"검색 결과 저장: {args.output}")
            else:
                print(result)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"HTTP Error {e.code}: {e.reason}")
        if error_body:
            print(error_body)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
