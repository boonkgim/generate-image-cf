#!/usr/bin/env bash
# Generate an image with Cloudflare Workers AI and save it to a file.
#
# Usage: generate-image.sh "<prompt>" [output-file] [model]
#
# Requires:
#   CLOUDFLARE_ACCOUNT_ID  - Cloudflare account ID
#   CLOUDFLARE_API_TOKEN   - API token with Workers AI permission
set -euo pipefail

PROMPT="${1:?Usage: generate-image.sh \"<prompt>\" [output-file] [model]}"
OUTPUT="${2:-output.png}"
MODEL="${3:-@cf/black-forest-labs/flux-1-schnell}"

: "${CLOUDFLARE_ACCOUNT_ID:?Set CLOUDFLARE_ACCOUNT_ID}"
: "${CLOUDFLARE_API_TOKEN:?Set CLOUDFLARE_API_TOKEN}"

URL="https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/ai/run/${MODEL}"

tmp_headers="$(mktemp)"
tmp_body="$(mktemp)"
trap 'rm -f "$tmp_headers" "$tmp_body"' EXIT

curl -sS -D "$tmp_headers" -o "$tmp_body" \
  -X POST "$URL" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg prompt "$PROMPT" '{prompt: $prompt}')"

content_type="$(grep -i '^content-type:' "$tmp_headers" | tail -1 | cut -d' ' -f2- | tr -d '\r')"

if [[ "$content_type" == image/* ]]; then
  # Some models (e.g. Stable Diffusion) return raw image bytes directly.
  cp "$tmp_body" "$OUTPUT"
else
  # Other models (e.g. Flux) return JSON with a base64-encoded image.
  if [[ "$(jq -r '.success' "$tmp_body")" != "true" ]]; then
    echo "Cloudflare API error:" >&2
    jq '.errors' "$tmp_body" >&2
    exit 1
  fi
  jq -r '.result.image' "$tmp_body" | base64 -d > "$OUTPUT"
fi

echo "Saved image to $OUTPUT"
