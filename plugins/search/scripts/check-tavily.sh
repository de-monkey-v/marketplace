#!/bin/bash
# Tavily API 상태 체크 스크립트
# Usage: check-tavily.sh
#
# 환경변수:
#   TAVILY_API_KEY - Tavily API key (필수)
#
# 출력:
#   JSON 형식의 응답 또는 에러 메시지

set -e

# API Key 확인
if [ -z "$TAVILY_API_KEY" ]; then
    echo '{"status": "error", "message": "TAVILY_API_KEY 환경변수가 설정되지 않았습니다"}'
    exit 1
fi

# 간단한 테스트 쿼리로 API 상태 확인
# max_results=1로 최소한의 결과만 요청
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST https://api.tavily.com/search \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $TAVILY_API_KEY" \
    -d '{
        "query": "test",
        "search_depth": "basic",
        "max_results": 1
    }' 2>&1)

# HTTP 상태 코드와 응답 본문 분리
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

# 결과 분석
if [ "$HTTP_CODE" = "200" ]; then
    # 응답에 results 필드가 있는지 확인
    if echo "$BODY" | jq -e '.results' > /dev/null 2>&1; then
        echo '{"status": "ok", "message": "Tavily API 연결 정상"}'
    else
        echo "{\"status\": \"error\", \"message\": \"예상치 못한 응답 형식\", \"response\": $BODY}"
    fi
elif [ "$HTTP_CODE" = "401" ]; then
    echo '{"status": "error", "message": "API Key가 유효하지 않습니다 (401 Unauthorized)"}'
elif [ "$HTTP_CODE" = "403" ]; then
    echo '{"status": "error", "message": "API 접근이 거부되었습니다 (403 Forbidden)"}'
elif [ "$HTTP_CODE" = "429" ]; then
    echo '{"status": "error", "message": "API 호출 한도 초과 (429 Too Many Requests)"}'
elif [ -z "$HTTP_CODE" ] || [ "$HTTP_CODE" = "000" ]; then
    echo '{"status": "error", "message": "네트워크 연결 실패"}'
else
    echo "{\"status\": \"error\", \"message\": \"HTTP 오류: $HTTP_CODE\", \"response\": $BODY}"
fi
