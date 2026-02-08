#!/bin/bash
# Tavily Search API - 고품질 웹 검색
# Usage: tavily-search.sh "query" [options]
#
# Options:
#   --depth DEPTH         basic | advanced (default: advanced)
#   --time TIME           day | week | month | year
#   --max-results N       최대 결과 수 (default: 10)
#   --include-domains D   특정 도메인만 검색 (쉼표 구분)
#   --exclude-domains D   특정 도메인 제외 (쉼표 구분)
#   --include-answer      AI 요약 답변 포함
#
# Examples:
#   tavily-search.sh "React 19 new features"
#   tavily-search.sh "TypeScript 5.0" --depth basic
#   tavily-search.sh "Next.js 15" --time month
#   tavily-search.sh "Python" --include-domains python.org,realpython.com

set -e

API_KEY="${TAVILY_API_KEY:?Error: TAVILY_API_KEY 환경변수를 설정하세요}"

# 기본값
SEARCH_DEPTH="advanced"
TIME_RANGE=""
MAX_RESULTS=10
INCLUDE_DOMAINS=""
EXCLUDE_DOMAINS=""
INCLUDE_ANSWER=false

# 첫 번째 인자가 --로 시작하지 않으면 쿼리
if [ -z "$1" ] || [[ "$1" == --* ]]; then
    echo "Usage: tavily-search.sh \"query\" [options]"
    echo ""
    echo "Options:"
    echo "  --depth DEPTH         basic | advanced (default: advanced)"
    echo "  --time TIME           day | week | month | year"
    echo "  --max-results N       최대 결과 수 (default: 10)"
    echo "  --include-domains D   특정 도메인만 검색 (쉼표 구분)"
    echo "  --exclude-domains D   특정 도메인 제외 (쉼표 구분)"
    echo "  --include-answer      AI 요약 답변 포함"
    echo ""
    echo "Backward compatibility:"
    echo "  tavily-search.sh \"query\" [depth] [time_range]"
    exit 1
fi

QUERY="$1"
shift

# 위치 인자 하위 호환성 체크
if [[ $# -gt 0 && ! "$1" == --* ]]; then
    if [[ "$1" == "basic" || "$1" == "advanced" ]]; then
        SEARCH_DEPTH="$1"
        shift
        if [[ $# -gt 0 && ! "$1" == --* ]]; then
            TIME_RANGE="$1"
            shift
        fi
    fi
fi

# 옵션 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        --depth)
            SEARCH_DEPTH="$2"
            shift 2
            ;;
        --time)
            TIME_RANGE="$2"
            shift 2
            ;;
        --max-results)
            MAX_RESULTS="$2"
            shift 2
            ;;
        --include-domains)
            INCLUDE_DOMAINS="$2"
            shift 2
            ;;
        --exclude-domains)
            EXCLUDE_DOMAINS="$2"
            shift 2
            ;;
        --include-answer)
            INCLUDE_ANSWER=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# JSON payload 생성
build_payload() {
    local payload=$(jq -n \
        --arg query "$QUERY" \
        --arg depth "$SEARCH_DEPTH" \
        --argjson max_results "$MAX_RESULTS" \
        --argjson include_answer "$INCLUDE_ANSWER" \
        '{query: $query, search_depth: $depth, max_results: $max_results, include_answer: $include_answer}')

    # time_range 추가
    if [ -n "$TIME_RANGE" ]; then
        payload=$(echo "$payload" | jq --arg time "$TIME_RANGE" '. + {time_range: $time}')
    fi

    # include_domains 추가
    if [ -n "$INCLUDE_DOMAINS" ]; then
        payload=$(echo "$payload" | jq --arg domains "$INCLUDE_DOMAINS" '. + {include_domains: ($domains | split(",") | map(. | gsub("^\\s+|\\s+$"; "")))}')
    fi

    # exclude_domains 추가
    if [ -n "$EXCLUDE_DOMAINS" ]; then
        payload=$(echo "$payload" | jq --arg domains "$EXCLUDE_DOMAINS" '. + {exclude_domains: ($domains | split(",") | map(. | gsub("^\\s+|\\s+$"; "")))}')
    fi

    echo "$payload"
}

PAYLOAD=$(build_payload)

curl -s -X POST https://api.tavily.com/search \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $API_KEY" \
    -d "$PAYLOAD" | jq .
