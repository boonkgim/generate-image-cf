#!/usr/bin/env python3
"""Generate an image with Cloudflare Workers AI and save it to a file.

Usage: generate_image.py "<prompt>" [output-file] [model]

Requires:
  CLOUDFLARE_ACCOUNT_ID - Cloudflare account ID
  CLOUDFLARE_API_TOKEN  - API token with Workers AI permission
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_MODEL = "@cf/black-forest-labs/flux-1-schnell"


def main():
    parser = argparse.ArgumentParser(description="Generate an image via Cloudflare Workers AI")
    parser.add_argument("prompt")
    parser.add_argument("output", nargs="?", default="output.png")
    parser.add_argument("model", nargs="?", default=DEFAULT_MODEL)
    args = parser.parse_args()

    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not account_id:
        sys.exit("Set CLOUDFLARE_ACCOUNT_ID")
    if not api_token:
        sys.exit("Set CLOUDFLARE_API_TOKEN")

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{args.model}"
    body = json.dumps({"prompt": args.prompt}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request) as response:
            content_type = response.headers.get("Content-Type", "")
            data = response.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"Cloudflare API error ({e.code}): {e.read().decode('utf-8', 'replace')}")

    if content_type.startswith("image/"):
        # Some models (e.g. Stable Diffusion) return raw image bytes directly.
        image_bytes = data
    else:
        # Other models (e.g. Flux) return JSON with a base64-encoded image.
        payload = json.loads(data)
        if not payload.get("success"):
            sys.exit(f"Cloudflare API error: {payload.get('errors')}")
        image_bytes = base64.b64decode(payload["result"]["image"])

    with open(args.output, "wb") as f:
        f.write(image_bytes)

    print(f"Saved image to {args.output}")


if __name__ == "__main__":
    main()
