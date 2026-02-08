#!/bin/bash
# Tavily Crawl & Save - 웹사이트 크롤링 후 마크다운 저장
# Usage: tavily-crawl-save.sh "url" [options]
#
# Options:
#   --output-dir DIR      저장 디렉토리 (default: ./crawled_context)
#   --max-depth N         크롤링 깊이 (default: 2)
#   --max-breadth N       각 페이지당 링크 폭 (default: 10)
#   --limit N             최대 페이지 수 (default: 50)
#   --extract-depth DEPTH basic | advanced (default: advanced)
#
# Examples:
#   tavily-crawl-save.sh "https://docs.nextjs.org"
#   tavily-crawl-save.sh "https://react.dev" --output-dir ./react-docs
#   tavily-crawl-save.sh "https://vitejs.dev" --limit 20

set -e

API_KEY="${TAVILY_API_KEY:?Error: TAVILY_API_KEY 환경변수를 설정하세요}"

# 기본값
OUTPUT_DIR="./crawled_context"
MAX_DEPTH=2
MAX_BREADTH=10
LIMIT=50
EXTRACT_DEPTH="advanced"

# 첫 번째 인자가 URL인지 확인
if [ -z "$1" ] || [[ "$1" == --* ]]; then
    echo "Usage: tavily-crawl-save.sh \"url\" [options]"
    echo ""
    echo "Options:"
    echo "  --output-dir DIR      저장 디렉토리 (default: ./crawled_context)"
    echo "  --max-depth N         크롤링 깊이 (default: 2)"
    echo "  --max-breadth N       각 페이지당 링크 폭 (default: 10)"
    echo "  --limit N             최대 페이지 수 (default: 50)"
    echo "  --extract-depth DEPTH basic | advanced (default: advanced)"
    exit 1
fi

URL="$1"
shift

# 옵션 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        --output-dir|-o)
            OUTPUT_DIR="$2"
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
        --extract-depth)
            EXTRACT_DEPTH="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# 도메인 추출
DOMAIN=$(echo "$URL" | sed -E 's|https?://([^/]+).*|\1|')
SAVE_DIR="${OUTPUT_DIR}/${DOMAIN}"

echo "크롤링 시작: $URL"
echo "저장 위치: $SAVE_DIR"

# 디렉토리 생성
mkdir -p "$SAVE_DIR"

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

# API 호출
RESPONSE=$(curl -s -X POST https://api.tavily.com/crawl \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $API_KEY" \
    -d "$PAYLOAD")

# 결과에서 페이지 추출하여 마크다운으로 저장
SAVED_COUNT=0
TIMESTAMP=$(date -Iseconds)

# results 또는 pages 배열 처리
PAGES=$(echo "$RESPONSE" | jq -r '.results // .pages // []')

echo "$PAGES" | jq -c '.[]' | while read -r page; do
    PAGE_URL=$(echo "$page" | jq -r '.url // ""')
    TITLE=$(echo "$page" | jq -r '.title // ""')
    CONTENT=$(echo "$page" | jq -r '.raw_content // .content // ""')

    if [ -z "$CONTENT" ]; then
        continue
    fi

    # URL을 파일명으로 변환
    FILENAME=$(echo "$PAGE_URL" | sed -E 's|https?://[^/]+/?||' | sed 's|/|_|g' | sed 's|[<>:"/\\|?*]|_|g')
    if [ -z "$FILENAME" ]; then
        FILENAME="index"
    fi
    FILENAME="${FILENAME:0:200}.md"

    FILEPATH="${SAVE_DIR}/${FILENAME}"

    # 마크다운 파일 생성
    cat > "$FILEPATH" << EOF
---
title: "${TITLE}"
source: "${PAGE_URL}"
crawled_at: "${TIMESTAMP}"
---

# ${TITLE}

${CONTENT}
EOF

    echo "  저장: $FILEPATH"
    SAVED_COUNT=$((SAVED_COUNT + 1))
done

# 요약 정보 저장
SUMMARY_PATH="${SAVE_DIR}/_crawl_summary.json"
jq -n \
    --arg url "$URL" \
    --arg crawled_at "$TIMESTAMP" \
    --argjson max_depth "$MAX_DEPTH" \
    --argjson max_breadth "$MAX_BREADTH" \
    --argjson limit "$LIMIT" \
    --arg extract_depth "$EXTRACT_DEPTH" \
    '{
        url: $url,
        crawled_at: $crawled_at,
        options: {
            max_depth: $max_depth,
            max_breadth: $max_breadth,
            limit: $limit,
            extract_depth: $extract_depth
        }
    }' > "$SUMMARY_PATH"

echo ""
echo "완료!"
echo "위치: $SAVE_DIR"
echo "요약: $SUMMARY_PATH"
