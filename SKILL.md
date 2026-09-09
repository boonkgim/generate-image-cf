---
name: generate-image-cf
description: Generate an image from a text prompt using Cloudflare Workers AI. Use when the user asks to generate, create, or produce an image (or AI art) via Cloudflare or Cloudflare Workers AI.
license: MIT
---

# Generate image (Cloudflare Workers AI)

Generate an image from a text prompt using a Cloudflare Workers AI text-to-image model
and save it as a local file.

## Prerequisites

Two environment variables must be set:

- `CLOUDFLARE_ACCOUNT_ID` - the Cloudflare account ID.
- `CLOUDFLARE_API_TOKEN` - an API token with the "Workers AI" permission.

If either is missing, ask the user for it (or how to find it in the Cloudflare
dashboard) before proceeding. Do not print token values back to the user.

### Getting the credentials via browser automation

If the agent has browser automation available (e.g. Claude Code's `claude-in-chrome`)
and the user's browser is already logged into Cloudflare, offer to fetch both values
directly instead of asking the user to copy them by hand:

1. Navigate to `https://dash.cloudflare.com/`. If more than one account is listed, ask
   the user which one to use, don't guess.
2. Click into that account. The account ID is the 32-character hex string in the
   resulting URL (`dash.cloudflare.com/<account-id>/...`) — no need to hunt for it in
   the Overview sidebar.
3. Navigate to `https://dash.cloudflare.com/profile/api-tokens`. Existing tokens'
   values can never be viewed again after creation, so an existing "Workers AI"-scoped
   token is not reusable; a new one must be created.
4. Creating a token modifies the user's account, so confirm first: name (e.g. the
   skill name), scope (`Account` -> `Workers AI` -> `Read` is enough), and which
   account. Only proceed once the user agrees.
5. Click "Create Token", use the built-in "Workers AI" template (or a custom token
   with that one permission), and submit.
6. Read the token value off the confirmation page (shown once). Use it directly to set
   up the environment variable (see `README.md`'s Setup section for where it can go:
   Claude Code's `settings.json`, or the shell) — never print the raw token value in
   chat.

`python3` (macOS/Linux) or `python` (Windows) must be available on the system. The
script uses only the standard library, so no `pip install` is needed.

## Steps

1. Confirm the prompt to render. If the user only gave a vague idea, write a clear,
   descriptive prompt before generating.
2. Pick an output path. Default to a `.png` file named after the prompt (kebab-case) in
   the current directory unless the user specifies one.
3. Run the script (`python3` on macOS/Linux, `python` on Windows):

   ```bash
   python3 scripts/generate_image.py "<prompt>" "<output-file>" ["<model>"]
   ```

   Model defaults to `@cf/black-forest-labs/flux-1-schnell` (best output quality of the
   models tested). If the account's 10,000/day free neuron allocation runs out on that
   model, the script automatically falls back to `@cf/bytedance/stable-diffusion-xl-lightning`,
   which is not neuron-metered, so generation keeps working for the rest of the day. Other
   useful models:
   - `@cf/stabilityai/stable-diffusion-xl-base-1.0`
   - `@cf/lykon/dreamshaper-8-lcm`
   - `@cf/bytedance/stable-diffusion-xl-lightning`

4. Report the saved file path to the user, and mention if the fallback model was used
   (the script prints this to stderr). If the script errors for any other reason, surface
   the Cloudflare API error message rather than retrying blindly.

## Notes

- Different models return the image differently (raw bytes vs. JSON with base64) -
  `scripts/generate_image.py` already handles both, so prefer it over ad-hoc requests.
- The script is pure Python standard library, so it runs the same way on macOS, Linux,
  and Windows.
- `flux-1-schnell` costs real neurons (~173/image at default settings, confirmed via the
  API's `cf-ai-neurons` header); `stable-diffusion-xl-base-1.0`, `stable-diffusion-xl-lightning`,
  and `dreamshaper-8-lcm` are all confirmed unmetered (0 neurons), so they don't draw down
  the daily budget at all.
- Full model list and parameters: https://developers.cloudflare.com/workers-ai/models/
  (filter by task "Text-to-Image").
