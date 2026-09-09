# generate-image-cf

**Turn a text prompt into a saved image file, straight from your coding agent, using
Cloudflare Workers AI.** No dashboard round-trip, no npm install, no guessing which model
is actually free.

An [agent skill](https://agentskills.io) for Claude Code, Codex, and any other AI coding
agent that reads `SKILL.md`. Ask for an image, and it writes a clear prompt, calls the
Workers AI API, and saves the result, defaulting to the best-quality model and falling
back automatically once the free daily budget runs out.

This repo's own [commit history](https://github.com/boonkgim/generate-image-cf/commits/main)
is the skill's design record, including the live API testing that corrected the numbers
below. Read it before you install anything.

## Why you would want this

- **Zero dependencies.** `scripts/generate_image.py` uses only the Python standard
  library, no `pip install`, so it runs identically on macOS, Linux, and Windows via
  `python3`/`python`.
- **Handles both response shapes Workers AI returns.** Some models return raw image
  bytes, others return JSON with a base64 string. Naive integrations trip on this; the
  script detects and handles both.
- **Defaults to quality, falls back to free.** Generation starts on `flux-1-schnell`
  (the best output quality tested) and automatically retries on the unmetered
  `stable-diffusion-xl-lightning` the moment Cloudflare reports the daily free neuron
  budget is exhausted, so it keeps working for the rest of the day at no extra cost.
- **Numbers calibrated against the real API, not just the docs.** Cloudflare's per-model
  pricing page describes "neurons per tile" and "neurons per step" as if they add, but
  live testing (the `cf-ai-neurons` response header) showed they multiply. The model
  comparison below reflects the corrected, verified cost, not the docs' literal wording.

## Install

Paste this to your agent:

```
install the skill at https://github.com/boonkgim/generate-image-cf
```

It clones the repo and puts `SKILL.md` and `scripts/` where your tool looks for skills.
To update it later, ask the same way, or `git pull` in the clone.

<details>
<summary>By hand</summary>

```bash
git clone https://github.com/boonkgim/generate-image-cf.git

# Claude Code
ln -s "$PWD/generate-image-cf" ~/.claude/skills/generate-image-cf

# Codex
ln -s "$PWD/generate-image-cf" ~/.agents/skills/generate-image-cf
```

Symlink into a project's `.claude/skills/` instead to scope it to one repo. Other tools
read skills from their own location, and some take an upload; check yours.

</details>

A skill is instructions your agent will follow, so read `SKILL.md` before installing this
or any other. It is one file, plus the `generate_image.py` script it runs.

## Works with

`SKILL.md` follows the [Agent Skills](https://agentskills.io) open standard, so it loads
directly in any agent that reads the format — **Claude Code**, from `~/.claude/skills/`,
**OpenAI Codex**, from `~/.agents/skills/`, and any other tool with its own skills
directory. Where a tool does not read `SKILL.md` natively, paste it into the session or
drop it into the rules file that tool already reads, such as `AGENTS.md`. Nothing in it
is tool-specific: the whole skill is prose and a standalone Python script.

## Setup

The skill needs two environment variables:

- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`

### 1. Get your account ID

1. Log in to the [Cloudflare dashboard](https://dash.cloudflare.com).
2. Pick any domain/account, then look at the right sidebar of the **Overview** page (or
   **Workers & Pages** &rarr; **Overview**) for **Account ID**. Copy it.

### 2. Create an API token

1. Go to **My Profile** &rarr; **API Tokens** &rarr; **Create Token**
   (https://dash.cloudflare.com/profile/api-tokens).
2. Choose **Create Custom Token**.
3. Under **Permissions**, add: `Account` &rarr; `Workers AI` &rarr; `Read` (or `Edit`).
4. Create the token and copy it immediately, you won't be able to view it again.

### 3. Set the environment variables

There are two ways to do this: via Claude Code's own `settings.json`, or directly in
your shell. Either way, only ever put your *actual* token in a location that never gets
committed, listed below.

#### Option A: Claude Code settings.json

Claude Code reads environment variables from an `env` object in its own settings files.
Put yours in one of these two, neither of which is ever committed:

| File | Scope |
|------|-------|
| `~/.claude/settings.json` | your user, every project |
| `.claude/settings.local.json` | this project, just you (already git-ignored here) |

Do not use `.claude/settings.json` for this: unlike the two files above, that one is
meant to be committed and shared with the team, so a real token placed there would leak
to anyone who clones the repo.

```json
{
  "env": {
    "CLOUDFLARE_ACCOUNT_ID": "your-account-id",
    "CLOUDFLARE_API_TOKEN": "your-api-token"
  }
}
```

Restart Claude Code (or start a new session) for the new file to be picked up.

#### Option B: shell environment

**macOS / Linux (bash or zsh)**

```bash
export CLOUDFLARE_ACCOUNT_ID="your-account-id"
export CLOUDFLARE_API_TOKEN="your-api-token"
```

Add those two lines to `~/.bashrc`, `~/.zshrc`, or `~/.profile` to persist them across
sessions. These files live outside the repo, so they are never committed either.

**Windows (PowerShell)**

```powershell
$env:CLOUDFLARE_ACCOUNT_ID = "your-account-id"
$env:CLOUDFLARE_API_TOKEN = "your-api-token"
```

To persist them across sessions, set them permanently instead:

```powershell
[System.Environment]::SetEnvironmentVariable("CLOUDFLARE_ACCOUNT_ID", "your-account-id", "User")
[System.Environment]::SetEnvironmentVariable("CLOUDFLARE_API_TOKEN", "your-api-token", "User")
```

**Windows (cmd)**

```cmd
setx CLOUDFLARE_ACCOUNT_ID "your-account-id"
setx CLOUDFLARE_API_TOKEN "your-api-token"
```

`setx` persists the variable, but only takes effect in new terminal windows.

## Usage

Ask for an image however you normally would. Tools that support invoking a skill by name
take `/generate-image-cf` directly.

```bash
python3 scripts/generate_image.py "a red fox in the snow" fox.png
```

This should write `fox.png` to the current directory. The skill writes a clear,
descriptive prompt if you only gave a vague idea, defaults to `flux-1-schnell`, and falls
back to the free `stable-diffusion-xl-lightning` automatically if the daily neuron budget
runs out. It never commits.

If this is useful, a ⭐ helps other people find it.

## Choosing a model

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

Notes:
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

## When not to use this

- **You need an input image (editing, inpainting, img2img).** This skill only does
  text-to-image. `stable-diffusion-v1-5-img2img` and `-inpainting` exist on Workers AI
  but aren't wired up here.
- **You need guaranteed, bounded latency.** Free-tier neuron exhaustion triggers a
  fallback to a different model, which changes output characteristics mid-session; a
  production pipeline with strict consistency requirements should pin one model instead.
- **You're already inside a Cloudflare Worker.** Call the [Workers AI
  binding](https://developers.cloudflare.com/workers-ai/) directly rather than going
  through this REST-API script.

## Author

Built by **Khur Boon Kgim** at [boonkgim.com](https://boonkgim.com), where I write about
practical AI for builders: AI agents, coding workflows, and shipping software.

## License

MIT. See [LICENSE](LICENSE).
