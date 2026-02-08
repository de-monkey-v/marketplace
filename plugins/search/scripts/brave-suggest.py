#!/usr/bin/env python3
"""Brave Suggest API - 검색어 추천
Usage: brave-suggest.py "query" [options]

Options:
  --count N       추천 수 (1-20, default: 5)
  --lang CODE     언어 (default: en)
  --country CODE  국가 코드 (default: US)
  --rich          리치 결과 포함 (설명, 이미지 등)
  --output FILE   결과를 파일로 저장

Examples:
  brave-suggest.py "how to"
  brave-suggest.py "python" --count 10
  brave-suggest.py "react" --rich
  brave-suggest.py "맛집" --lang ko --country KR
"""
import sys
import os
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error

API_KEY = os.environ.get("BRAVE_API_KEY", "")
BASE_URL = "https://api.search.brave.com/res/v1/suggest/search"


def main():
    parser = argparse.ArgumentParser(
        description="Brave Suggest API - 검색어 추천",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("query", help="검색 쿼리")
    parser.add_argument("--count", type=int, default=5,
                        help="추천 수 (1-20, default: 5)")
    parser.add_argument("--lang", default="en",
                        help="언어 (default: en)")
    parser.add_argument("--country", default="US",
                        help="국가 코드 (default: US)")
    parser.add_argument("--rich", action="store_true",
                        help="리치 결과 포함 (설명, 이미지 등)")
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
        "lang": args.lang,
        "country": args.country,
    }

    if args.rich:
        params["rich"] = "true"

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
                print(f"검색어 추천 결과 저장: {args.output}")
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
