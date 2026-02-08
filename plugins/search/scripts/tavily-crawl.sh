#!/bin/bash
# Tavily Crawl API - 웹사이트 크롤링
# Usage: tavily-crawl.sh "url" [options]
#
# Options:
#   --extract-depth DEPTH  basic | advanced (default: advanced)
#   --max-depth N          크롤링 깊이 (default: 2)
#   --max-breadth N        각 페이지당 링크 폭 (default: 10)
#   --limit N              최대 페이지 수 (default: 50)
#
# Examples:
#   tavily-crawl.sh "https://docs.nextjs.org"
#   tavily-crawl.sh "https://react.dev" --max-depth 3 --limit 100
#   tavily-crawl.sh "https://vitejs.dev" --extract-depth basic

set -e

API_KEY="${TAVILY_API_KEY:?Error: TAVILY_API_KEY 환경변수를 설정하세요}"

# 기본값
EXTRACT_DEPTH="advanced"
MAX_DEPTH=2
MAX_BREADTH=10
LIMIT=50

# 첫 번째 인자가 URL인지 확인
if [ -z "$1" ] || [[ "$1" == --* ]]; then
    echo "Usage: tavily-crawl.sh \"url\" [options]"
    echo ""
    echo "Options:"
    echo "  --extract-depth DEPTH  basic | advanced (default: advanced)"
    echo "  --max-depth N          크롤링 깊이 (default: 2)"
    echo "  --max-breadth N        각 페이지당 링크 폭 (default: 10)"
    echo "  --limit N              최대 페이지 수 (default: 50)"
    echo ""
    echo "Backward compatibility:"
    echo "  tavily-crawl.sh \"url\" [extract_depth]"
    exit 1
fi

URL="$1"
shift

# 위치 인자 하위 호환성 체크
if [[ $# -gt 0 && ! "$1" == --* ]]; then
    if [[ "$1" == "basic" || "$1" == "advanced" ]]; then
        EXTRACT_DEPTH="$1"
        shift
    fi
fi

# 옵션 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        --extract-depth)
            EXTRACT_DEPTH="$2"
            shift 2
            ;;
        --max-depth)
            MAX_DEPTH="$2"
            shift 2
            ;;
        --max-breadth)
            MAX_BREADTH="$2"
            shift 2
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# JSON payload 생성
PAYLOAD=$(jq -n \
    --arg url "$URL" \
    --arg extract_depth "$EXTRACT_DEPTH" \
    --argjson max_depth "$MAX_DEPTH" \
    --argjson max_breadth "$MAX_BREADTH" \
    --argjson limit "$LIMIT" \
    '{
        url: $url,
        extract_depth: $extract_depth,
        max_depth: $max_depth,
        max_breadth: $max_breadth,
        limit: $limit
    }')

curl -s -X POST https://api.tavily.com/crawl \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $API_KEY" \
    -d "$PAYLOAD" | jq .
