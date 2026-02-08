#!/bin/bash
# Tavily Research API - AI 종합 연구
# Usage: tavily-research.sh "query" [options]
#
# Options:
#   --model MODEL         mini | pro | auto (default: auto)
#   --max-results N       최대 결과 수 (default: 10)
#   --no-citations        인용 제외
#
# Examples:
#   tavily-research.sh "React Server Components 아키텍처"
#   tavily-research.sh "Python 비동기 프로그래밍 패턴" --model pro

set -e

API_KEY="${TAVILY_API_KEY:?Error: TAVILY_API_KEY 환경변수를 설정하세요}"

# 기본값
MODEL="auto"
MAX_RESULTS=10
INCLUDE_CITATIONS=true

# 첫 번째 인자가 --로 시작하지 않으면 쿼리
if [ -z "$1" ] || [[ "$1" == --* ]]; then
    echo "Usage: tavily-research.sh \"query\" [options]"
    echo ""
    echo "Options:"
    echo "  --model MODEL         mini | pro | auto (default: auto)"
    echo "  --max-results N       최대 결과 수 (default: 10)"
    echo "  --no-citations        인용 제외"
    echo ""
    echo "Examples:"
    echo "  tavily-research.sh \"React Server Components 아키텍처\""
    echo "  tavily-research.sh \"Python 패턴\" --model pro"
    exit 1
fi

QUERY="$1"
shift

# 옵션 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        --model)
            MODEL="$2"
            shift 2
            ;;
        --max-results)
            MAX_RESULTS="$2"
            shift 2
            ;;
        --no-citations)
            INCLUDE_CITATIONS=false
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# JSON payload 생성 (Research API는 'input' 파라미터 사용)
PAYLOAD=$(jq -n \
    --arg input "$QUERY" \
    --arg model "$MODEL" \
    --argjson max_results "$MAX_RESULTS" \
    --argjson include_citations "$INCLUDE_CITATIONS" \
    '{
        input: $input,
        model: $model,
        max_results: $max_results,
        include_citations: $include_citations
    }')

curl -s -X POST https://api.tavily.com/research \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $API_KEY" \
    -d "$PAYLOAD" | jq .
