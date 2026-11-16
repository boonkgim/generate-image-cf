# Choosing a model

The script defaults to `@cf/black-forest-labs/flux-1-schnell`. Its REST endpoint
accepts a JSON `prompt` and returns a base64 image, which the script decodes.
An explicit model argument replaces that default; verify its current availability,
request format and pricing before use. The script supports JSON prompt requests
and image or JSON/base64 responses, not multipart requests.

## Quota exhaustion

On HTTP 429 with error code 4006, the script exits with a clear quota message.
It makes no second request and does not change models. Wait for the allocation to
reset, or review the account plan and budget before retrying. Other API errors
are reported without retrying as well.

The former automatic fallback, `@cf/bytedance/stable-diffusion-xl-lightning`,
retires on 20 November 2026. The previously suggested
`@cf/stabilityai/stable-diffusion-xl-base-1.0` and `@cf/lykon/dreamshaper-8-lcm`
retire on the same date. Do not use them for new requests.

Cloudflare suggests `@cf/black-forest-labs/flux-2-klein-9b` as a replacement,
but its documented request format is multipart. It is not a drop-in replacement
for this script's JSON request, and it must not be assumed to bypass the account's
quota or to be free. No automatic replacement is configured.

## Current references

Verified 16 November 2026; consult these sources again before changing models:

- [Retirement notice](https://developers.cloudflare.com/changelog/post/2026-11-05-planned-model-deprecations/)
- [Flux Schnell request and response schema](https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/)
- [Flux Klein 9B request schema](https://developers.cloudflare.com/workers-ai/models/flux-2-klein-9b/)
- [Model catalogue](https://developers.cloudflare.com/workers-ai/models/)
- [Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/)
