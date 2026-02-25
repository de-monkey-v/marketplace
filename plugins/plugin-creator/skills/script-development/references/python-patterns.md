# Python Script Patterns

## Script Template

```python
#!/usr/bin/env python3
"""
script-name.py — Brief description

Usage:
    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/script-name.py <query> [options]

Options:
    query           Search query (required)
    --count N       Result count (default: 10)
    --output FMT    Output format: json|text (default: json)

Environment:
    API_KEY         Required API key
"""

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def parse_args():
    parser = argparse.ArgumentParser(description="Brief description")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--count", type=int, default=10, help="Result count")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                        help="Output format")
    return parser.parse_args()


def main():
    args = parse_args()

    # Validate environment
    api_key = os.environ.get("API_KEY")
    if not api_key:
        print("ERROR: API_KEY environment variable is required", file=sys.stderr)
        sys.exit(1)

    # Main logic
    result = do_work(args.query, args.count, api_key)

    # Output
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for item in result.get("items", []):
            print(f"- {item['title']}: {item['url']}")


def do_work(query, count, api_key):
    """Core logic implementation."""
    # ... implementation ...
    return {"items": [], "total": 0}


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
```

## Argument Parsing with argparse

```python
# Positional + optional arguments
parser = argparse.ArgumentParser(description="Tool description")
parser.add_argument("input", help="Input file or query")
parser.add_argument("-o", "--output", default="result.json", help="Output path")
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
parser.add_argument("--format", choices=["json", "csv", "text"], default="json")
parser.add_argument("--limit", type=int, default=100)

# Subcommands
subparsers = parser.add_subparsers(dest="command", required=True)
search_parser = subparsers.add_parser("search", help="Search items")
search_parser.add_argument("query")
list_parser = subparsers.add_parser("list", help="List items")
```

## HTTP Requests with urllib

```python
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

def api_get(url, headers=None, timeout=30):
    """Make GET request and return parsed JSON."""
    req = Request(url, headers=headers or {})
    try:
        with urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)

def api_post(url, data, headers=None, timeout=30):
    """Make POST request with JSON body."""
    body = json.dumps(data).encode()
    req = Request(url, data=body, headers={
        "Content-Type": "application/json",
        **(headers or {})
    })
    try:
        with urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"HTTP {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
```

## JSON Processing

```python
import json

# Read JSON from file
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

# Read JSON from stdin (Hook Pattern A)
input_data = json.loads(sys.stdin.read())

# Write JSON to stdout
print(json.dumps(result, indent=2, ensure_ascii=False))

# Transform data
items = [
    {"title": item["name"], "url": item["link"], "score": item.get("score", 0)}
    for item in data.get("results", [])
    if item.get("score", 0) > 0.5
]
```

## Subprocess Execution

```python
import subprocess

# Safe execution (no shell=True)
result = subprocess.run(
    ["git", "status", "--porcelain"],
    capture_output=True, text=True, check=True
)
print(result.stdout)

# With timeout
try:
    result = subprocess.run(
        ["command", "arg1"],
        capture_output=True, text=True, check=True, timeout=30
    )
except subprocess.TimeoutExpired:
    print("Command timed out", file=sys.stderr)
    sys.exit(1)
except subprocess.CalledProcessError as e:
    print(f"Command failed: {e.stderr}", file=sys.stderr)
    sys.exit(e.returncode)
```

## Temporary File Handling

```python
import tempfile
import os

# Temp file with automatic cleanup
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=True) as f:
    json.dump(data, f)
    f.flush()
    # Use f.name while in context

# Temp directory
with tempfile.TemporaryDirectory() as tmpdir:
    filepath = os.path.join(tmpdir, "output.json")
    # Use tmpdir, auto-cleaned on exit
```

## Path Handling

```python
import os

# Use CLAUDE_PLUGIN_ROOT
plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
config_path = os.path.join(plugin_root, "config", "settings.json")
scripts_dir = os.path.join(plugin_root, "scripts")

# Safe path joining (prevents traversal)
def safe_path(base, *parts):
    result = os.path.normpath(os.path.join(base, *parts))
    if not result.startswith(os.path.normpath(base)):
        raise ValueError(f"Path traversal detected: {result}")
    return result
```

## Error Handling Pattern

```python
class ScriptError(Exception):
    """Base error for script failures."""
    def __init__(self, message, exit_code=1):
        super().__init__(message)
        self.exit_code = exit_code

def main():
    try:
        args = parse_args()
        result = process(args)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except ScriptError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)
```
