# generate-image-cf

Agent skill that generates images from a text prompt using Cloudflare Workers AI.

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

### 4. Verify

```bash
python3 scripts/generate_image.py "a red fox in the snow" fox.png
```

This should write `fox.png` to the current directory. See `SKILL.md` for how the agent
uses the script.
