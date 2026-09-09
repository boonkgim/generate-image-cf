# Choosing a model

Cloudflare Workers AI free plan gives you 10,000 neurons/day; paid is $0.011 per 1,000
neurons with no daily cap (bounded instead by a 720 requests/min rate limit). Cost per
image varies enormously by model, so picking one is a real quality-vs-quantity trade-off.

The rows below marked **verified** were confirmed against the live API's `cf-ai-neurons`
response header; the rest are estimates computed from Cloudflare's published pricing and
should be treated as order-of-magnitude, not exact.

| Model | Neurons/image | Free tier: images/day | Paid: images per $1 |
|---|---|---|---|
| `stable-diffusion-xl-lightning` | **verified: 0** | unlimited (rate-limit bound) | free |
| `dreamshaper-8-lcm` | **verified: 0** | unlimited | free |
| `stable-diffusion-xl-base-1.0` | **verified: 0** | unlimited | free |
| `flux-1-schnell` (default, 4 steps, 1024x1024) | **verified: 172.8** | ~58 | ~526 |
| `flux-2-klein-9b` | ~1,364 (1024x1024) | ~7 | ~67 |
| `phoenix-1.0` | ~3,120 (1024x1024, 25 steps) | ~3 | ~29 |
| `lucid-origin` | ~4,380 (1120x1120, ~20 steps) | ~2 | ~21 |
| `flux-2-dev` | ~4,500 (1024x1024, ~20 steps) | ~2 | ~20 |
| `flux-2-klein-4b` | **unverified** &mdash; its `multipart` request schema isn't documented clearly enough to get a working request | unknown | unknown |

## Notes

- **The script defaults to `flux-1-schnell`** (best output quality of the models
  tested here) **and automatically falls back to `stable-diffusion-xl-lightning`**
  once the account's 10,000/day free neuron allocation is used up on it (Cloudflare
  returns HTTP 429, error code 4006), so generation keeps working for the rest of the
  day at no extra cost. No action needed; the script prints a note to stderr when this
  happens.
- Cloudflare's per-model docs describe cost as separate "neurons per tile" and "neurons
  per step" rates, which reads as additive, but live testing shows they multiply:
  `neurons = tiles x (tile_rate + steps x step_rate)`. The `flux-1-schnell` row above
  already reflects this correction (confirmed at both the default 4 steps and at the max
  of 8 steps); `phoenix-1.0` and `lucid-origin` use the same corrected formula but with
  assumed (undocumented) step counts, so treat those two as rougher estimates.
- Full list and per-model parameters: https://developers.cloudflare.com/workers-ai/models/
  Pricing: https://developers.cloudflare.com/workers-ai/platform/pricing/
