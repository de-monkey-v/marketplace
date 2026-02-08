#!/bin/bash
# Tavily Extract API
# Usage: tavily-extract.sh "url1" ["url2" "url3" ...]
#   Extract content from one or more URLs

set -e

API_KEY="${TAVILY_API_KEY:?Error: TAVILY_API_KEY 환경변수를 설정하세요}"

if [ -z "$1" ]; then
    echo "Usage: tavily-extract.sh \"url1\" [\"url2\" \"url3\" ...]"
    echo "  Extract content from one or more URLs"
    exit 1
fi

# Build URLs array
URLS_JSON=$(printf '%s\n' "$@" | jq -R . | jq -s .)

PAYLOAD=$(jq -n --argjson urls "$URLS_JSON" '{urls: $urls}')

curl -s -X POST https://api.tavily.com/extract \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $API_KEY" \
    -d "$PAYLOAD" | jq .
