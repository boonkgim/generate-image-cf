# generate-image-cf

**Turn a text prompt into a saved image file, straight from your coding agent, using
Cloudflare Workers AI.** No dashboard round-trip, no npm install, no guessing which model
is actually free.

An [agent skill](https://agentskills.io) for Claude Code, Codex, and any other AI coding
agent that reads `SKILL.md`. Ask for an image, and it writes a clear prompt, calls the
Workers AI API, and saves the result, defaulting to the best-quality model and falling
back automatically once the free daily budget runs out.

This repo's own [commit history](https://github.com/boonkgim/generate-image-cf/commits/main)
is the skill's design record, including the live API testing that corrected the model
costs in [docs/MODELS.md](docs/MODELS.md). Read it before you install anything.

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
  live testing (the `cf-ai-neurons` response header) showed they multiply. See
  [docs/MODELS.md](docs/MODELS.md) for the corrected, verified cost of every model.

## Quick start

Three prompts, pasted to your agent one at a time, are the whole happy path: no manual
dashboard clicking, no copying env vars yourself.

**1. Install**

```
install the skill at https://github.com/boonkgim/generate-image-cf
```

It clones the repo and puts `SKILL.md` and `scripts/` where your tool looks for skills.

**2. Set up credentials**

```
get my Cloudflare account ID and a Workers AI API token for generate-image-cf by driving my browser, then set them up
```

This needs your agent's browser automation (e.g. Claude Code's `claude-in-chrome`) and an
already-logged-in Cloudflare session in that browser. It'll ask which account to use if
you have more than one, and confirm before creating anything.

**3. Generate an image**

```
generate an image of a red fox in the snow using generate-image-cf
```

(Tools that support invoking a skill by name take `/generate-image-cf` directly.) If
that produced a file, you're done.

No browser automation, or no agent at all? [docs/SETUP.md](docs/SETUP.md) covers
installing and setting up credentials by hand, and running the script directly.

## Works with

`SKILL.md` follows the [Agent Skills](https://agentskills.io) open standard, so it loads
directly in any agent that reads the format — **Claude Code**, from `~/.claude/skills/`,
**OpenAI Codex**, from `~/.agents/skills/`, and any other tool with its own skills
directory. Where a tool does not read `SKILL.md` natively, paste it into the session or
drop it into the rules file that tool already reads, such as `AGENTS.md`. Nothing in it
is tool-specific: the whole skill is prose and a standalone Python script.

If this is useful, a ⭐ helps other people find it.

## Choosing a model

The script defaults to `flux-1-schnell` for quality and falls back to the free
`stable-diffusion-xl-lightning` once the daily neuron budget runs out, so you rarely need
to think about this. If you want to pick deliberately, [docs/MODELS.md](docs/MODELS.md)
has the full cost-per-image comparison across every supported model, verified against the
live API rather than taken at face value from Cloudflare's docs.

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
