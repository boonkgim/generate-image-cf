# Manual setup

[Quick start](../README.md#quick-start) installs the skill and sets up credentials for
you. This page is the manual alternative: doing any part of it by hand, or without an
agent at all.

## Install by hand

```bash
git clone https://github.com/boonkgim/generate-image-cf.git

# Claude Code
ln -s "$PWD/generate-image-cf" ~/.claude/skills/generate-image-cf

# Codex
ln -s "$PWD/generate-image-cf" ~/.agents/skills/generate-image-cf
```

Symlink into a project's `.claude/skills/` instead to scope it to one repo. Other tools
read skills from their own location, and some take an upload; check yours.

## Get credentials

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

### Option A: Claude Code settings.json

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

### Option B: shell environment

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

## Running the script directly

Once the environment variables are set, you don't need an agent at all:

```bash
python3 scripts/generate_image.py "a red fox in the snow" fox.png
```

This writes `fox.png` to the current directory.

## What the browser-automation step does

Quick start step 2 asks the agent to drive the browser instead of you clicking through
the steps above by hand. If the agent supports browser automation (e.g. Claude Code's
`claude-in-chrome`) and your browser is already logged into Cloudflare, it will:

1. Navigate to `https://dash.cloudflare.com/`. If more than one account is listed, it
   asks you which one to use rather than guessing.
2. Click into that account. The account ID is the 32-character hex string in the
   resulting URL (`dash.cloudflare.com/<account-id>/...`), so there's no need to hunt
   for it in the Overview sidebar.
3. Navigate to `https://dash.cloudflare.com/profile/api-tokens`. Existing tokens'
   values can never be viewed again after creation, so an existing "Workers AI"-scoped
   token is not reusable; a new one has to be created.
4. Confirm with you first, since creating a token modifies your account: the name,
   scope (`Account` &rarr; `Workers AI` &rarr; `Read` is enough), and which account.
5. Click "Create Token", use the built-in "Workers AI" template (or a custom token with
   that one permission), and submit.
6. Read the token value off the confirmation page (shown once) and use it directly to
   set up the environment variable, without ever printing the raw value in chat.

See `SKILL.md` for the source of these instructions.
