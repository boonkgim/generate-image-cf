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
# Not neuron-metered (confirmed via the cf-ai-neurons response header), so it keeps
# working once the 10,000/day free neuron allocation on DEFAULT_MODEL runs out.
FALLBACK_MODEL = "@cf/bytedance/stable-diffusion-xl-lightning"
NEURON_ALLOCATION_EXHAUSTED_CODE = 4006


def call_model(account_id, api_token, model, prompt):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
    body = json.dumps({"prompt": prompt}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request) as response:
        return response.headers.get("Content-Type", ""), response.read()


def is_neuron_allocation_exhausted(http_error_body):
    try:
        payload = json.loads(http_error_body)
    except json.JSONDecodeError:
        return False
    return any(
        err.get("code") == NEURON_ALLOCATION_EXHAUSTED_CODE
        for err in payload.get("errors", [])
    )


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

    model = args.model
    try:
        content_type, data = call_model(account_id, api_token, model, args.prompt)
    except urllib.error.HTTPError as e:
        error_body = e.read()
        if e.code == 429 and model != FALLBACK_MODEL and is_neuron_allocation_exhausted(error_body):
            print(
                f"Daily free neuron allocation used up on {model}; "
                f"falling back to {FALLBACK_MODEL} (not neuron-metered).",
                file=sys.stderr,
            )
            model = FALLBACK_MODEL
            try:
                content_type, data = call_model(account_id, api_token, model, args.prompt)
            except urllib.error.HTTPError as e2:
                sys.exit(f"Cloudflare API error ({e2.code}): {e2.read().decode('utf-8', 'replace')}")
        else:
            sys.exit(f"Cloudflare API error ({e.code}): {error_body.decode('utf-8', 'replace')}")

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
