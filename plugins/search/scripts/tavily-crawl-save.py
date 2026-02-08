#!/usr/bin/env python3.9
"""Tavily Crawl & Save - 웹사이트 크롤링 후 마크다운 저장
Usage: tavily-crawl-save.py "url" [options]

Options:
  --output-dir DIR      저장 디렉토리 (default: ./crawled_context)
  --max-depth N         크롤링 깊이 (default: 2)
  --max-breadth N       각 페이지당 링크 폭 (default: 10)
  --limit N             최대 페이지 수 (default: 50)
  --extract-depth DEPTH basic | advanced (default: advanced)

Examples:
  tavily-crawl-save.py "https://docs.nextjs.org"
  tavily-crawl-save.py "https://react.dev" --output-dir ./react-docs
  tavily-crawl-save.py "https://vitejs.dev" --limit 20
"""
import sys
import os
import json
import argparse
import re
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path

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


def sanitize_filename(url: str) -> str:
    """URL을 안전한 파일명으로 변환"""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        path = "index"
    # 특수문자 제거
    filename = re.sub(r'[<>:"/\\|?*]', '_', path)
    filename = filename.replace("/", "_")
    return filename[:200]  # 파일명 길이 제한


def save_as_markdown(page: dict, output_dir: Path, domain: str) -> str:
    """페이지를 마크다운 파일로 저장"""
    url = page.get("url", "")
    content = page.get("raw_content", "") or page.get("content", "")
    title = page.get("title", url)

    if not content:
        return None

    filename = sanitize_filename(url) + ".md"
    filepath = output_dir / domain / filename

    # 디렉토리 생성
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # 프론트매터 생성
    frontmatter = f"""---
title: "{title}"
source: "{url}"
crawled_at: "{datetime.now().isoformat()}"
---

"""

    # 마크다운 파일 저장
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.write(f"# {title}\n\n")
        f.write(content)

    return str(filepath)


def main():
    parser = argparse.ArgumentParser(
        description="Tavily Crawl & Save - 웹사이트 크롤링 후 마크다운 저장",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("url", help="크롤링할 URL")
    parser.add_argument("--output-dir", "-o", default="./crawled_context",
                        help="저장 디렉토리 (default: ./crawled_context)")
    parser.add_argument("--max-depth", type=int, default=2,
                        help="크롤링 깊이 (default: 2)")
    parser.add_argument("--max-breadth", type=int, default=10,
                        help="각 페이지당 링크 폭 (default: 10)")
    parser.add_argument("--limit", type=int, default=50,
                        help="최대 페이지 수 (default: 50)")
    parser.add_argument("--extract-depth", choices=["basic", "advanced"], default="advanced",
                        help="추출 깊이 (default: advanced)")

    args = parser.parse_args()

    client = TavilyClient(API_KEY)
    output_dir = Path(args.output_dir)
    domain = urlparse(args.url).netloc

    print(f"크롤링 시작: {args.url}")
    print(f"저장 위치: {output_dir / domain}")

    # 출력 디렉토리 미리 생성
    (output_dir / domain).mkdir(parents=True, exist_ok=True)

    try:
        # Crawl API 호출
        response = client.crawl(
            url=args.url,
            max_depth=args.max_depth,
            max_breadth=args.max_breadth,
            limit=args.limit,
            extract_depth=args.extract_depth
        )

        # 결과에서 페이지 추출
        pages = response.get("results", [])
        if not pages:
            pages = response.get("pages", [])
        if not pages and isinstance(response, list):
            pages = response

        saved_files = []
        for page in pages:
            filepath = save_as_markdown(page, output_dir, domain)
            if filepath:
                saved_files.append(filepath)
                print(f"  저장: {filepath}")

        print(f"\n완료: {len(saved_files)}개 파일 저장")
        print(f"위치: {output_dir / domain}")

        # 요약 정보 저장
        summary = {
            "url": args.url,
            "crawled_at": datetime.now().isoformat(),
            "total_pages": len(saved_files),
            "files": saved_files,
            "options": {
                "max_depth": args.max_depth,
                "max_breadth": args.max_breadth,
                "limit": args.limit,
                "extract_depth": args.extract_depth
            }
        }

        summary_path = output_dir / domain / "_crawl_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"요약: {summary_path}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
