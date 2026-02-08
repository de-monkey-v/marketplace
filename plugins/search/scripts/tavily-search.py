#!/usr/bin/env python3.9
"""Tavily Search API - 고품질 웹 검색
Usage: tavily-search.py "query" [options]

Options:
  --depth DEPTH         basic | advanced (default: advanced)
  --time TIME           day | week | month | year
  --max-results N       최대 결과 수 (default: 10)
  --include-domains D   특정 도메인만 검색 (쉼표 구분)
  --exclude-domains D   특정 도메인 제외 (쉼표 구분)
  --include-answer      AI 요약 답변 포함
  --output FILE         결과를 파일로 저장

Examples:
  tavily-search.py "React 19 new features"
  tavily-search.py "TypeScript 5.0" --depth basic
  tavily-search.py "Next.js 15" --time month
  tavily-search.py "Python tutorial" --include-domains python.org,realpython.com
  tavily-search.py "security best practices" --exclude-domains medium.com
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
        description="Tavily Search API - 고품질 웹 검색",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("query", help="검색 쿼리")
    parser.add_argument("--depth", choices=["basic", "advanced"], default="advanced",
                        help="검색 깊이 (default: advanced)")
    parser.add_argument("--time", choices=["day", "week", "month", "year"],
                        help="시간 범위")
    parser.add_argument("--max-results", type=int, default=10,
                        help="최대 결과 수 (default: 10)")
    parser.add_argument("--include-domains",
                        help="특정 도메인만 검색 (쉼표 구분)")
    parser.add_argument("--exclude-domains",
                        help="특정 도메인 제외 (쉼표 구분)")
    parser.add_argument("--include-answer", action="store_true",
                        help="AI 요약 답변 포함")
    parser.add_argument("--output", "-o", help="결과를 파일로 저장")

    # 하위 호환성: 위치 인자로도 depth, time 지원
    args, unknown = parser.parse_known_args()

    # 위치 인자 처리 (하위 호환성)
    if unknown:
        if len(unknown) >= 1 and unknown[0] in ["basic", "advanced"]:
            args.depth = unknown[0]
        if len(unknown) >= 2 and unknown[1] in ["day", "week", "month", "year"]:
            args.time = unknown[1]

    client = TavilyClient(API_KEY)

    kwargs = {
        "query": args.query,
        "search_depth": args.depth,
        "max_results": args.max_results,
    }

    if args.time:
        kwargs["time_range"] = args.time

    if args.include_domains:
        kwargs["include_domains"] = [d.strip() for d in args.include_domains.split(",")]

    if args.exclude_domains:
        kwargs["exclude_domains"] = [d.strip() for d in args.exclude_domains.split(",")]

    if args.include_answer:
        kwargs["include_answer"] = True

    try:
        response = client.search(**kwargs)
        result = json.dumps(response, indent=2, ensure_ascii=False)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"검색 결과 저장: {args.output}")
        else:
            print(result)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
