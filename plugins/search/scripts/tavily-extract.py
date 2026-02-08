#!/usr/bin/env python3.9
"""Tavily Extract API
Usage: tavily-extract.py "url1" ["url2" "url3" ...]
  Extract content from one or more URLs
"""
import sys
import os
import json
from tavily import TavilyClient

API_KEY = os.environ.get("TAVILY_API_KEY")
if not API_KEY:
    print("Error: TAVILY_API_KEY 환경변수를 설정하세요")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    urls = sys.argv[1:]

    client = TavilyClient(API_KEY)
    response = client.extract(urls=urls)
    print(json.dumps(response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
