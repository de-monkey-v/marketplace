#!/usr/bin/env python3.9
"""Tavily Crawl API - 웹사이트 크롤링
Usage: tavily-crawl.py "url" [options]

Options:
  --extract-depth DEPTH  basic | advanced (default: advanced)
  --max-depth N          크롤링 깊이 (default: 2)
  --max-breadth N        각 페이지당 링크 폭 (default: 10)
  --limit N              최대 페이지 수 (default: 50)
  --output FILE          결과를 파일로 저장

Examples:
  tavily-crawl.py "https://docs.nextjs.org"
  tavily-crawl.py "https://react.dev" --max-depth 3 --limit 100
  tavily-crawl.py "https://vitejs.dev" --extract-depth basic
"""
import sys
import os
import json
import argparse

try:
    from tavily import TavilyClient
except ImportError:
    print("Error: tavily-python 패키지가 필요합니다.")
    print("설치: pip install tavily-python")
    sys.exit(1)

API_KEY = os.environ.get("TAVILY_API_KEY")
if not API_KEY:
    print("Error: TAVILY_API_KEY 환경변수를 설정하세요")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Tavily Crawl API - 웹사이트 크롤링",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("url", help="크롤링할 URL")
    parser.add_argument("--extract-depth", choices=["basic", "advanced"], default="advanced",
                        help="추출 깊이 (default: advanced)")
    parser.add_argument("--max-depth", type=int, default=2,
                        help="크롤링 깊이 (default: 2)")
    parser.add_argument("--max-breadth", type=int, default=10,
                        help="각 페이지당 링크 폭 (default: 10)")
    parser.add_argument("--limit", type=int, default=50,
                        help="최대 페이지 수 (default: 50)")
    parser.add_argument("--output", "-o", help="결과를 파일로 저장")

    # 하위 호환성: 위치 인자로도 depth 지원
    args, unknown = parser.parse_known_args()

    # 위치 인자 처리 (하위 호환성)
    if unknown and unknown[0] in ["basic", "advanced"]:
        args.extract_depth = unknown[0]

    client = TavilyClient(API_KEY)

    try:
        response = client.crawl(
            url=args.url,
            extract_depth=args.extract_depth,
            max_depth=args.max_depth,
            max_breadth=args.max_breadth,
            limit=args.limit
        )
        result = json.dumps(response, indent=2, ensure_ascii=False)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"크롤링 결과 저장: {args.output}")
        else:
            print(result)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
