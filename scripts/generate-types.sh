#!/usr/bin/env bash
# Generate types from JSON Schema for both Python (Pydantic) and TypeScript
# Usage: ./scripts/generate-types.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

SCHEMAS_DIR="$ROOT_DIR/shared/schemas"
PYTHON_OUTPUT="$ROOT_DIR/backend/api/nonagon_api/generated"
TS_OUTPUT="$ROOT_DIR/frontend/src/types/generated"

echo "=== Nonagon Type Generator ==="
echo "Schemas: $SCHEMAS_DIR"
echo ""

# Ensure output directories exist
mkdir -p "$PYTHON_OUTPUT"
mkdir -p "$TS_OUTPUT"

# Generate Python Pydantic models
echo "📦 Generating Python Pydantic models..."
if command -v datamodel-codegen &> /dev/null; then
    datamodel-codegen \
        --input "$SCHEMAS_DIR" \
        --output "$PYTHON_OUTPUT/schemas.py" \
        --input-file-type jsonschema \
        --output-model-type pydantic_v2.BaseModel \
        --target-python-version 3.11 \
        --use-annotated \
        --field-constraints \
        --capitalise-enum-members \
        --use-double-quotes \
        --collapse-root-models
    echo "✅ Python models generated: $PYTHON_OUTPUT/schemas.py"
else
    echo "⚠️  datamodel-codegen not found. Install with: pip install datamodel-code-generator"
    echo "   Skipping Python generation."
fi

# Create Python __init__.py
cat > "$PYTHON_OUTPUT/__init__.py" << 'EOF'
# AUTO-GENERATED - DO NOT EDIT
# Generated from shared/schemas/*.json
# Regenerate with: ./scripts/generate-types.sh

from .schemas import *
EOF

# Generate TypeScript types
echo ""
echo "📦 Generating TypeScript types..."
if command -v npx &> /dev/null; then
    # Generate individual files for each schema
    for schema in "$SCHEMAS_DIR"/*.schema.json; do
        filename=$(basename "$schema" .schema.json)
        npx json-schema-to-typescript \
            "$schema" \
            --output "$TS_OUTPUT/$filename.ts" \
            --bannerComment "/* AUTO-GENERATED - DO NOT EDIT */
/* Generated from shared/schemas/$filename.schema.json */
/* Regenerate with: ./scripts/generate-types.sh */" \
            --cwd "$SCHEMAS_DIR" \
            2>/dev/null || echo "⚠️  Failed to generate $filename.ts (may have unresolved refs)"
    done
    
    # Create index.ts to export all types
    cat > "$TS_OUTPUT/index.ts" << 'EOF'
/* AUTO-GENERATED - DO NOT EDIT */
/* Regenerate with: ./scripts/generate-types.sh */

export * from './common';
export * from './enums';
export * from './user';
export * from './quest';
export * from './character';
export * from './summary';
EOF
    echo "✅ TypeScript types generated: $TS_OUTPUT/"
else
    echo "⚠️  npx not found. Install Node.js to generate TypeScript types."
    echo "   Skipping TypeScript generation."
fi

echo ""
echo "=== Generation Complete ==="
