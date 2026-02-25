# Bash Script Patterns

## Script Template

```bash
#!/bin/bash
set -euo pipefail

# ============================================================
# script-name.sh — Brief description
# Usage: bash ${CLAUDE_PLUGIN_ROOT}/scripts/script-name.sh [options] <args>
# Options:
#   -q QUERY    Search query
#   -c COUNT    Result count (default: 10)
#   -o FORMAT   Output format: json|text (default: json)
#   -h          Show help
# Environment:
#   API_KEY     Required API key
# ============================================================

readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# --- Defaults ---
COUNT=10
OUTPUT="json"

# --- Functions ---
usage() {
  sed -n '/^# Usage:/,/^# ===/p' "$0" | sed 's/^# //'
}

die() {
  echo "ERROR: $1" >&2
  exit "${2:-1}"
}

log() {
  echo "[$SCRIPT_NAME] $*" >&2
}

# --- Argument Parsing ---
while getopts "q:c:o:h" opt; do
  case $opt in
    q) QUERY="$OPTARG" ;;
    c) COUNT="$OPTARG" ;;
    o) OUTPUT="$OPTARG" ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done
shift $((OPTIND - 1))

# --- Validation ---
[[ -z "${QUERY:-}" ]] && die "Query is required (-q)"
command -v jq >/dev/null 2>&1 || die "jq is required"

# --- Main Logic ---
# ... implementation here ...
```

## Argument Parsing with getopts

```bash
# Named options
while getopts "v:f:n:h" opt; do
  case $opt in
    v) VERSION="$OPTARG" ;;
    f) FILE="$OPTARG" ;;
    n) NAME="$OPTARG" ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

# Positional args after options
shift $((OPTIND - 1))
POSITIONAL_ARG="${1:-}"
```

## JSON Processing with jq

```bash
# Parse JSON field
VALUE=$(echo "$JSON" | jq -r '.field')

# Array iteration
echo "$JSON" | jq -r '.items[] | "\(.name)\t\(.value)"' | while IFS=$'\t' read -r name value; do
  echo "Name: $name, Value: $value"
done

# Build JSON output
jq -n \
  --arg query "$QUERY" \
  --arg count "$COUNT" \
  '{query: $query, count: ($count | tonumber), timestamp: now | todate}'

# Filter and transform
echo "$RESPONSE" | jq '[.results[] | {title: .title, url: .url, score: .score}]'
```

## HTTP Requests with curl

```bash
# GET with headers
RESPONSE=$(curl -sS -f \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  "$BASE_URL/endpoint" 2>&1) || die "API request failed: $RESPONSE"

# POST with JSON body
RESPONSE=$(curl -sS -f \
  -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\", \"count\": $COUNT}" \
  "$BASE_URL/search" 2>&1) || die "Search failed: $RESPONSE"

# With timeout and retry
curl -sS -f --retry 3 --retry-delay 2 --max-time 30 \
  -H "Authorization: Bearer $API_KEY" \
  "$BASE_URL/endpoint"
```

## Temporary Files

```bash
# Safe temp file creation
TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT

# Temp directory
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# Write and process
curl -sS "$URL" > "$TMPFILE"
jq '.results' "$TMPFILE"
```

## Color Output

```bash
# Color definitions (respect NO_COLOR)
if [[ -z "${NO_COLOR:-}" ]] && [[ -t 1 ]]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[0;33m'
  BLUE='\033[0;34m'
  NC='\033[0m'
else
  RED='' GREEN='' YELLOW='' BLUE='' NC=''
fi

# Usage
echo -e "${GREEN}Success:${NC} Operation completed"
echo -e "${RED}Error:${NC} Something failed" >&2
echo -e "${YELLOW}Warning:${NC} Check configuration"
```

## Common Patterns

### Environment Variable Check
```bash
: "${API_KEY:?API_KEY environment variable is required}"
```

### File Existence Check
```bash
[[ -f "$CONFIG_FILE" ]] || die "Config file not found: $CONFIG_FILE"
```

### Dependency Check
```bash
for cmd in jq curl; do
  command -v "$cmd" >/dev/null 2>&1 || die "$cmd is required but not installed"
done
```

### Safe String Operations
```bash
# Always quote variables
FILE_PATH="${BASE_DIR}/${FILE_NAME}"
grep -r "${SEARCH_TERM}" "${TARGET_DIR}"

# Default values
TIMEOUT="${TIMEOUT:-30}"
FORMAT="${FORMAT:-json}"
```
