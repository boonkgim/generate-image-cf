# generate-image-cf

An [agent skill](https://agentskills.io) that generates an image from a text prompt
using Cloudflare Workers AI, called directly from your AI agent.

It sharpens a vague prompt, generates the image, and saves it locally. Uses the
highest-quality model by default; switches automatically to a free model once the daily
quota runs out.

## Quick start

Paste these three prompts to your agent, one at a time.

**1. Install**

```
install the skill at https://github.com/boonkgim/generate-image-cf
```

Clones the repo and puts `SKILL.md` and `scripts/` where your tool looks for skills.

**2. Set up credentials**

```
get my Cloudflare account ID and a Workers AI API token for generate-image-cf by driving my browser, then set them up
```

Requires your agent's browser automation (e.g. Claude Code's `claude-in-chrome`) and an
already-logged-in Cloudflare session. It asks which account to use if you have more than
one, and confirms before creating the API token.

**3. Generate an image**

```
generate an image of a red fox in the snow using generate-image-cf
```

Tools that support invoking a skill by name take `/generate-image-cf` directly.

No browser automation, or no agent at all? [docs/SETUP.md](docs/SETUP.md) covers
installing and setting up credentials by hand, and running the script directly.

## Works with

Any AI agent that reads the open [Agent Skills](https://agentskills.io) standard,
including:

- **Claude Code**
- **OpenAI Codex**
- **OpenClaw**
- **Hermes**
- **claude.ai** and the **Claude Agent SDK** (by upload)

If your tool doesn't support skills natively, paste `SKILL.md`'s contents into the
session instead.

## When not to use this

You need an input image (editing, inpainting, img2img). This skill only does
text-to-image.

## More detail

- [docs/SETUP.md](docs/SETUP.md) &mdash; account ID and API token by hand, where to put
  them, and running the script without an agent.
- [docs/MODELS.md](docs/MODELS.md) &mdash; cost per image for every supported model,
  verified against the live API.

## Author

Built by **Khur Boon Kgim** ([boonkgim.com](https://boonkgim.com)).

## License

MIT. See [LICENSE](LICENSE).
