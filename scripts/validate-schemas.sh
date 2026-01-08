#!/usr/bin/env bash
# Validate JSON Schema files
# Usage: ./scripts/validate-schemas.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
SCHEMAS_DIR="$ROOT_DIR/shared/schemas"

echo "=== Validating JSON Schemas ==="

errors=0

for schema in "$SCHEMAS_DIR"/*.schema.json; do
    filename=$(basename "$schema")
    echo -n "Checking $filename... "
    
    # Check JSON syntax
    if ! python3 -c "import json; json.load(open('$schema'))" 2>/dev/null; then
        echo "❌ Invalid JSON"
        errors=$((errors + 1))
        continue
    fi
    
    # Check schema structure (basic validation)
    if ! python3 -c "
import json
with open('$schema') as f:
    data = json.load(f)
if '\$schema' not in data:
    raise ValueError('Missing \$schema')
if '\$id' not in data:
    raise ValueError('Missing \$id')
" 2>/dev/null; then
        echo "❌ Missing required fields"
        errors=$((errors + 1))
        continue
    fi
    
    echo "✅"
done

echo ""
if [ $errors -eq 0 ]; then
    echo "All schemas valid!"
    exit 0
else
    echo "Found $errors error(s)"
    exit 1
fi
