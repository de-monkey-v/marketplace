#!/usr/bin/env python3.9
"""Tavily Research API - AI 종합 연구
Usage: tavily-research.py "query" [options]

Options:
  --model MODEL         mini | pro | auto (default: auto)
  --max-results N       최대 결과 수 (default: 10)
  --include-citations   인용 포함 (default: true)
  --no-citations        인용 제외
  --output FILE         결과를 파일로 저장

Examples:
  tavily-research.py "React Server Components 아키텍처"
  tavily-research.py "Python 비동기 프로그래밍 패턴" --model pro
  tavily-research.py "Next.js 15 새 기능" --output research.json
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
        description="Tavily Research API - AI 종합 연구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "React Server Components 아키텍처"
  %(prog)s "Python 비동기 프로그래밍 패턴" --model pro
  %(prog)s "Next.js 15 새 기능" --output research.json
        """
    )
    parser.add_argument("query", help="연구 주제 쿼리")
    parser.add_argument("--model", choices=["mini", "pro", "auto"], default="auto",
                        help="모델 선택: mini(빠름), pro(심층), auto(자동)")
    parser.add_argument("--max-results", type=int, default=10,
                        help="최대 결과 수 (default: 10)")
    parser.add_argument("--include-citations", dest="citations", action="store_true",
                        default=True, help="인용 포함 (default)")
    parser.add_argument("--no-citations", dest="citations", action="store_false",
                        help="인용 제외")
    parser.add_argument("--output", "-o", help="결과를 파일로 저장")

    args = parser.parse_args()

    client = TavilyClient(API_KEY)

    try:
        # Research API 호출 (input 파라미터 사용)
        response = client.research(
            input=args.query,
            model=args.model,
            max_results=args.max_results,
            include_citations=args.citations
        )

        result = json.dumps(response, indent=2, ensure_ascii=False)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"연구 결과 저장: {args.output}")
        else:
            print(result)

    except AttributeError:
        # research 메서드가 없는 경우 (구버전 tavily-python)
        print("Error: research API는 최신 tavily-python이 필요합니다.")
        print("업그레이드: pip install --upgrade tavily-python")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
