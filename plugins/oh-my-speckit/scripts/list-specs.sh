#!/bin/bash
# list-specs.sh - List all spec files in .specify/specs/
#
# Usage: list-specs.sh [PROJECT_ROOT]
#
# If PROJECT_ROOT is not provided, auto-detects by walking up
# from cwd looking for .specify/, package.json, .git, etc.

set -euo pipefail

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

# --- PROJECT_ROOT detection ---
find_project_root() {
    local dir="${1:-$(pwd)}"
    # Resolve to absolute path
    dir="$(cd "$dir" 2>/dev/null && pwd)" || return 1

    while [[ "$dir" != "/" ]]; do
        [[ -d "$dir/.specify" ]] && echo "$dir" && return 0
        for f in package.json pyproject.toml Cargo.toml go.mod; do
            [[ -f "$dir/$f" ]] && echo "$dir" && return 0
        done
        [[ -d "$dir/.git" ]] && echo "$dir" && return 0
        dir="$(dirname "$dir")"
    done
    return 1
}

if [[ -n "${1:-}" ]]; then
    PROJECT_ROOT="$1"
    if [[ ! -d "$PROJECT_ROOT" ]]; then
        echo -e "${RED}Error: Directory not found: $PROJECT_ROOT${RESET}" >&2
        exit 1
    fi
else
    if ! PROJECT_ROOT="$(find_project_root)"; then
        echo -e "${RED}Error: PROJECT_ROOT를 찾을 수 없습니다.${RESET}" >&2
        echo -e "${DIM}cwd부터 .specify/, package.json, .git을 탐색했지만 찾지 못했습니다.${RESET}" >&2
        exit 1
    fi
fi

SPECS_DIR="${PROJECT_ROOT}/.specify/specs"

# --- No specs directory ---
if [[ ! -d "$SPECS_DIR" ]]; then
    echo -e "${YELLOW}No .specify/specs/ directory found at ${PROJECT_ROOT}${RESET}"
    echo -e "${DIM}Run /oh-my-speckit:specify [feature] to create your first spec.${RESET}"
    exit 0
fi

# --- Collect spec directories ---
mapfile -t spec_dirs < <(find "$SPECS_DIR" -maxdepth 1 -mindepth 1 -type d -name '[0-9][0-9][0-9]-*' 2>/dev/null | sort)

if [[ ${#spec_dirs[@]} -eq 0 ]]; then
    echo -e "${YELLOW}No specs found in .specify/specs/${RESET}"
    echo -e "${DIM}Run /oh-my-speckit:specify [feature] to create one.${RESET}"
    exit 0
fi

# --- Extract metadata from spec.md ---
extract_field() {
    local file="$1" pattern="$2"
    grep -m1 "$pattern" "$file" 2>/dev/null | sed "s/.*$pattern[[:space:]]*//" | sed 's/^[[:space:]]*//' || echo "-"
}

# --- Build table data ---
declare -a rows=()
declare -A status_counts=()

for dir in "${spec_dirs[@]}"; do
    dir_name="$(basename "$dir")"
    spec_id="${dir_name%%-*}"
    feature_name="${dir_name#*-}"

    spec_file="$dir/spec.md"
    has_plan="N"
    [[ -f "$dir/plan.md" ]] && has_plan="Y"

    status="-"
    priority="-"
    created="-"

    if [[ -f "$spec_file" ]]; then
        status="$(extract_field "$spec_file" '\*\*Status\*\*:')"
        priority="$(extract_field "$spec_file" '\*\*Priority\*\*:')"
        created="$(extract_field "$spec_file" '\*\*Created\*\*:')"
    fi

    # Clean up extracted values
    [[ -z "$status" ]] && status="-"
    [[ -z "$priority" ]] && priority="-"
    [[ -z "$created" ]] && created="-"

    rows+=("${spec_id}|${feature_name}|${status}|${priority}|${has_plan}|${created}")

    if [[ "$status" != "-" ]]; then
        status_counts[$status]=$(( ${status_counts[$status]:-0} + 1 ))
    fi
done

# --- Print table ---
echo -e "${BOLD}Specs in:${RESET} ${CYAN}${SPECS_DIR}${RESET}"
echo ""

# Header
printf " ${BOLD}%-5s${RESET} | ${BOLD}%-28s${RESET} | ${BOLD}%-10s${RESET} | ${BOLD}%-8s${RESET} | ${BOLD}%-4s${RESET} | ${BOLD}%-10s${RESET}\n" \
    "ID" "Feature Name" "Status" "Priority" "Plan" "Created"
printf -- "------+------------------------------+------------+----------+------+------------\n"

# Rows
for row in "${rows[@]}"; do
    IFS='|' read -r id feature st pri plan crt <<< "$row"

    # Color status
    case "$st" in
        Draft)       st_color="${YELLOW}" ;;
        Review)      st_color="${CYAN}" ;;
        Approved)    st_color="${GREEN}" ;;
        Implemented) st_color="${GREEN}" ;;
        *)           st_color="${RESET}" ;;
    esac

    # Color plan
    if [[ "$plan" == "Y" ]]; then
        plan_display="${GREEN}Y${RESET}"
    else
        plan_display="${DIM}N${RESET}"
    fi

    printf " %-5s | %-28s | ${st_color}%-10s${RESET} | %-8s | %-4b | %-10s\n" \
        "$id" "$feature" "$st" "$pri" "$plan_display" "$crt"
done

# Summary
echo ""
total=${#rows[@]}
summary="Total: ${total} spec"
[[ $total -ne 1 ]] && summary+="s"

if [[ ${#status_counts[@]} -gt 0 ]]; then
    parts=()
    for s in $(echo "${!status_counts[@]}" | tr ' ' '\n' | sort); do
        parts+=("${status_counts[$s]} ${s}")
    done
    summary+=" ($(IFS=', '; echo "${parts[*]}"))"
fi

echo -e "${BOLD}${summary}${RESET}"
