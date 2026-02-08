#!/usr/bin/env python3
"""Brave Spellcheck API - 맞춤법 검사
Usage: brave-spellcheck.py "query" [options]

Options:
  --lang CODE     언어 (default: en)
  --country CODE  국가 코드 (default: US)
  --output FILE   결과를 파일로 저장

Examples:
  brave-spellcheck.py "artifical inteligence"
  brave-spellcheck.py "프로그래밍" --lang ko
"""
import sys
import os
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error

API_KEY = os.environ.get("BRAVE_API_KEY", "")
BASE_URL = "https://api.search.brave.com/res/v1/spellcheck/search"


def main():
    parser = argparse.ArgumentParser(
        description="Brave Spellcheck API - 맞춤법 검사",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("query", help="맞춤법 검사할 텍스트")
    parser.add_argument("--lang", default="en",
                        help="언어 (default: en)")
    parser.add_argument("--country", default="US",
                        help="국가 코드 (default: US)")
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
        "lang": args.lang,
        "country": args.country,
    }

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
                print(f"맞춤법 검사 결과 저장: {args.output}")
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
