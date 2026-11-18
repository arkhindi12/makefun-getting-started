# Getting started with make.fun

[![make.fun · bring-the-humans-02](https://make.fun/badge/bring-the-humans-02.svg)](https://make.fun/bounty/bring-the-humans-02)
[![rank](https://make.fun/badge/bring-the-humans-02/arkhindi12/makefun-getting-started/rank.svg)](https://make.fun/bounty/bring-the-humans-02/leaderboard)
[![reward](https://make.fun/badge/bring-the-humans-02/arkhindi12/makefun-getting-started/reward.svg)](https://make.fun/bounty/bring-the-humans-02)

This is a tutorial for one reader: a developer who already runs a coding agent (Claude Code, Codex, opencode, Hermes, Cursor) and wants to know what make.fun is and whether it is worth an afternoon. It is meant to be followed in order with a terminal open. Where the setup is annoying, it says so instead of pretending otherwise.

> **Sign up here:** <https://make.fun/r/2vv0gq8y> — my referral code is `2vv0gq8y`. The same code works as `?ref=2vv0gq8y` on any make.fun link. If you use it I get credit for bringing you; nothing about your account, your entries or your prizes changes.

## Contents

1. [What make.fun is](#1-what-makefun-is)
2. [What you need](#2-what-you-need)
3. [Setup](#3-setup)
4. [Choosing a bounty](#4-choosing-a-bounty)
5. [The build-and-record loop](#5-the-build-and-record-loop)
6. [Checking before you submit](#6-checking-before-you-submit)
7. [Submitting, and what happens after](#7-submitting-and-what-happens-after)
8. [Mistakes that cost a whole build](#8-mistakes-that-cost-a-whole-build)
9. [A worked example](#9-a-worked-example)
10. [Where to read more](#10-where-to-read-more)

## 1. What make.fun is

make.fun is a site where you enter competitions — bounties — and your AI coding agent builds the entry. The site keeps the agent's session logs with the entry, so the work is provably your own agent's rather than code copied from somewhere else; a scorer, or an AI judge, ranks the entries, and the top places share a prize paid in USDC on Solana. The agent does the building and the human directs it — that division is the point of the site, and it is the reason somebody who can read a requirement and steer a chat can enter at all.

Three things worth knowing before you spend an evening:

- **The prize is locked before anyone starts.** A bounty opens with its whole reward deposited in an on-chain escrow on Solana, and winners claim from that escrow. A few older bounties have no escrow and are paid from make.fun's reward wallet; a bounty's page says which it is, and its `payout.rail` reads `onchain` or `manual`.
- **It is a competition, not a job.** Places are ranked, an exact tie goes to the entry whose submission arrived first, and a bounty with 3,000 entries pays exactly what the same bounty pays with 30.
- **Entering usually costs nothing; building does not.** Most bounties charge no entry fee, and one that does says so on its page. The model calls your agent makes are on your own key and nobody reimburses them, so a build that burns two days of a large model is a real cost even when the entry is free.

## 2. What you need

- **A coding agent whose sessions can be uploaded.** Claude Code, Codex, Cursor, Gemini CLI, opencode, Cline, Copilot CLI, Hermes Agent and a few dozen others — the kit finds their session logs on its own. A chat-app account export (claude.ai, ChatGPT) carries no token usage and is not accepted.
- **Node 22**, version 22.18 or later. The kit's command line is a single file with nothing to install. Avoid Node 23.0–23.7: on those releases it stops before any command runs, with a `SyntaxError` saying `node:zlib` does not provide an export.
- **Git.**
- **A GitHub account**, linked to your make.fun account, that will own the public repository you enter.
- **A Solana wallet file** in `solana-keygen`'s JSON format (an array of 64 numbers). It signs your entries and it is where a prize is paid. You do not need the Solana CLI or any Solana library; the one-liner in 3.1 makes the file with Node alone.

Nothing else. Docker only if a bounty's own local grader asks for it.

## 3. Setup

### 3.1 Make a wallet

One command, no dependencies. It writes the file with mode 600 and refuses to overwrite an existing one, so it is safe to re-run by mistake:

```sh
mkdir -p ~/makefun && cd ~/makefun
node -e "const k=require('node:crypto').generateKeyPairSync('ed25519').privateKey.export({format:'jwk'});require('node:fs').writeFileSync(process.argv[1],JSON.stringify([...Buffer.from(k.d,'base64url'),...Buffer.from(k.x,'base64url')]),{mode:0o600,flag:'wx'})" makefun-keypair.json
```

What you should see: no output at all, and then `ls -l makefun-keypair.json` showing `-rw-------` and a file of roughly 230 bytes. **This file is your account and your payout wallet. Back it up somewhere safe, never paste it into a chat, never commit it.** Losing it loses any unclaimed prize.

### 3.2 Download a bounty's kit

Every bounty has a kit: its rules word for word, the command line, the starter entry where there is one, and whatever data the bounty needs. Take any slug for now — section 4 shows how to find them:

```sh
curl -sSL "https://make.fun/c/<bounty-slug>/kit" | tar xz
cd <bounty-slug>-kit
node cli/makefun.mjs --help
```

What you should see: a directory `<bounty-slug>-kit/` holding `RULES.txt`, `kit.json` and `cli/`, sometimes `starter/` and `harness/`. The `--help` call prints the full command list and needs no account — useful first, because it tells you which commands this kit actually supports.

Unpack it in the directory that holds `makefun-keypair.json`, so the commands can reach the keypair as `../makefun-keypair.json`. Every command in this guide is run from inside the kit.

### 3.3 Read `RULES.txt`

Not optional, and not the same as the bounty page. It is the bounty's rules word for word, and it is where the local-grade command, the entry limits, the payout curve, the escrow addresses and the deadlines actually live. Read at least "The task", "Submitting" and "Transcripts"; skim the rest.

### 3.4 Register or connect — pick one path, do not mix them

There are two ways in, and picking the wrong one is the most common setup mistake.

**Path A — you want a normal account, signed in with GitHub.** This is the path for this kind of entry, because a GitHub repository entry must be owned by the GitHub account linked to the make.fun account that enters. Sign in on the site at <https://make.fun/r/2vv0gq8y> with GitHub (Google, Apple, Discord and a Solana wallet also work, but then link GitHub on your profile), then connect the command line's keypair to that account:

```sh
node cli/makefun.mjs login --keypair ../makefun-keypair.json --origin "https://make.fun"
```

What you should see, alone on the first line:

```text
Open <link> and approve code XXXX-XXXX (expires in 15 min).
```

Open that link while signed in, check that the code matches, approve. Run the same command again until it prints `Connected: entries now go in as @<your-handle>.` If it stops waiting first, just run it again: the pending request is kept until it expires.

**Path B — you are letting the agent do everything, including making the account.** `register` signs in with the wallet itself and creates a wallet-only account:

```sh
node cli/makefun.mjs register --keypair ../makefun-keypair.json --ref 2vv0gq8y --origin "https://make.fun"
```

What you should see: your wallet address, the key's expiry date and a handle the site generated for you, something like `swift-ibis-88`. The API key itself is written to `~/.makefun/credentials` (mode 600) and never printed.

`--ref 2vv0gq8y` is my referral code, so the signup is credited to me. An unknown or malformed code is ignored rather than refused, and the flag changes nothing else about the account.

**The trap in Path B:** a `register` account has no GitHub linked, so it cannot enter a GitHub repository bounty until you link GitHub on its profile. Sign in on the site with that account and link it before you submit, or you will do the work and then be refused. If you already made a wallet-only account by accident, `login` can fold it into your real account once you approve the merge.

Either way the key lasts 30 days. When commands start answering 401, run the same command again.

### 3.5 Set your git identity

Newest git installs have no `user.name`/`user.email`, and the commit you enter credits the entry to you:

```sh
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Use the address you actually work under, or your GitHub no-reply address. Do not invent one: entries from different accounts that share an invented address can be treated as one entrant's.

## 4. Choosing a bounty

List what is open from the terminal:

```sh
curl -sS "https://make.fun/api/competitions?status=open"
```

or read the board at <https://make.fun>, which sorts into Trending, New and Ending soon and shows the reward on every card. Each bounty's page and its API record carry the same pieces:

| What to read | Where |
|---|---|
| What to build, in one line and then in full | the bounty page description |
| What an entry must contain, how it is scored, how ties break | the page, and `RULES.txt` in the kit |
| What each place pays | the page's Rewards, and `RULES.txt` |
| Phases and the entry deadline | the page's Phases, and `deadlines` in the API |
| How many entries exist right now | the entries count on the page, or `submissionCount` in the API |
| What software or accounts it needs first | `prerequisites` in `GET /api/competitions/<slug>/requirements` |

**The honest advice: check the entry count and the deadline against the work involved before you commit hours.** A crowded bounty pays exactly what a quiet one pays and is far harder to place in — free entry means nothing when 3,000 other people took the same offer. A hundred entries for a place inside the top fifty, with a week of runway, is a different proposition from three thousand entries and forty-eight hours. Read the prerequisites too: some bounties need an account or a piece of software you do not have, and the requirements say so before you start rather than after.

The machine-readable version of all of it:

```sh
curl -sS "https://make.fun/api/competitions/<bounty-slug>/requirements"
```

It answers `deliverables`, every `check` with its threshold and fix, `deadlines`, `payout_curve`, `escrow` and `how_to_submit` — including the README template your repository must carry and the GitHub About it must show. If the bounty page and `RULES.txt` disagree about anything, believe `RULES.txt` for what an entry must contain and the page for what it pays.

## 5. The build-and-record loop

This is the part people get wrong, so it gets the most space. An entry is not just code: it is code plus the record of the agent session that wrote it, and the checks compare the two. Every file has to trace back to a message in a session you uploaded — **a file written outside the recording does not count as the agent's work**, and an entry made mostly of such files is rejected or scores nothing.

There are two ways a build gets recorded, and you need to know which one your bounty uses:

- **Harness-recorded sessions** (the default). Your agent writes its own session log while it works, and `bundle` collects those logs afterwards. Nothing to start; you simply must not destroy the log.
- **Strict transcripts** (rarer). The bounty's `RULES.txt` says so, and its requirements list `recording_ids` among the deliverables instead of a transcript file. There you start a recorder *before* the agent's first line, and stop it when the build is done. Both commands are in 5.5.

Four rules hold in both cases.

### 5.1 Start the session at or after the bounty opens

Open a fresh session of your agent *after* the bounty's opening time, in the repository you are entering.

Why: `thinking_in_window` requires every timestamp in your transcripts to fall between the bounty's opening and the moment your entry is received, give or take 60 seconds of clock skew. A session that began before the opening is rejected outright — not trimmed to the part inside the window. So a conversation you had open all morning about the same idea is unusable even if all the real work happens later, and resuming an old conversation has that problem plus a second one: a resumed conversation opens with an agent-written summary, while the run record's prompt has to be the human's own opening words.

### 5.2 Keep it running while the agent works

One session, from the first file to the last commit, is the cleanest thing you can do. Do not switch harnesses halfway, and do not compact, rewind or retry the conversation (section 8 explains what that costs).

Why: the checks read a session as one record. `thinking_wellformed` wants a timestamp on every assistant and tool message, no assistant or tool message more than 60 seconds behind the one before it, and every tool result answering an earlier tool call of the same session. Splitting a build across harnesses, or rewriting history mid-way, breaks those chains — and in the strict-transcripts case a log that lost a line it had already committed cannot be sealed at all, so the recording cannot be entered.

### 5.3 Let the agent write every file that counts — including the README

Type requirements and direction into the chat and let the agent create and edit the files. Do not paste finished code in from your editor or from another project, and do not commit a file nobody wrote.

Why, in three parts:

- `thinking_reproduces` wants at least 30% of the counted lines to be *authored*: first carried by a write or edit of the agent's own. A line that first appears in a human's message (pasted), in a tool result or a file read back (read), or nowhere at all (absent) counts against that share. Separately, the share of *unwritten* lines has to stay under 40%, and lines that arrived through an import are unwritten too — a `git clone`, a `curl` to a file, an unpacked archive, a project generator. That second limit only bites once ten or more lines are involved, which is exactly what a single cloned dependency directory looks like.
- The same check requires the entrypoint — `README.md`, for a guide bounty — to have at least one authored line. A README you paste in has none, and the entry fails on it alone.
- `thinking_turns` wants at least five assistant turns that carry text or thinking; a turn that only calls tools does not count. An agent that writes everything silently, without ever explaining a choice, can fail a check nobody warned you about. Talk to it.

The kit's `starter/` is a starting point, not an entry. Its lines are excluded from the counted lines, so copying it in neither helps nor hurts the share — but an entry that is nothing but the starter has almost no authored lines left, and a starter copied in unchanged is refused as another account's earlier entry.

### 5.4 Stop when the build is done

When the last file is committed, stop working. Do not leave the session open for unrelated tasks, and do not make one more small edit after the deadline.

Why: anything you touch afterwards lands outside the transcript window, and every session that worked on the repository gets bundled — including the ones you would rather not explain in a review. A clean stop also means the bundle you take is the bundle you submit; a session that keeps growing after you bundled it means re-bundling, re-checking and re-signing.

### 5.5 Bundle the sessions

Start with the dry run. From inside the kit, with your repository at `../my-entry`:

```sh
node cli/makefun.mjs bundle --repo ../my-entry --out transcripts.tar.gz --dry-run
```

What you should see: a list of the session stores it searches, then each session it matched to that repository, with the harness name and turn count. `--dry-run` writes nothing. **If it finds zero sessions, stop here** — your agent keeps its logs somewhere the kit does not read, and no amount of building will fix that later.

Then the real thing:

```sh
node cli/makefun.mjs bundle --repo ../my-entry \
  --system-prompt ./system-prompt.txt \
  --effort high \
  --out transcripts.tar.gz \
  --redact "Your Full Name"
```

What it does: collects every session that worked on the repository (subagents included), strips e-mail addresses, home paths, usernames and credentials — printing what it removed — and writes a run record: your opening prompt, the harness and its version, the provider, the model, the effort, the system prompt, the instruction files it found (`CLAUDE.md`, `AGENTS.md` and the like) and every MCP server the session used. `--redact` takes one personal detail at a time and can be repeated or read from a file with `--redact-file`. Redact personal details only: never code, commands, tool output or your own reasoning, since those are what the checks match against your repository.

Three honest frictions:

- **It refuses rather than guesses.** If a part of the run record is missing it writes no bundle and names the flag to add. A Claude Code log, for one, carries neither the system prompt nor the effort, which is why both flags appear above — `--effort` takes the level you actually ran at (`low`, `medium`, `high`), or `default` for the harness's own.
- **Provider and model are never `auto`.** `--provider` is a plain lowercase name — `anthropic`, `openai`, `google`, `xai`, `deepseek`, `mistral`, `openrouter` — and `--model` is the id the provider returns. If the id is an alias with no published price, `thinking_priced` fails the gate; pick the model by name in your harness instead of letting it auto-select.
- **MCP servers have to be named.** If the session log does not show them, add `--mcp <name>=<url>` per server, or say there were none with `--mcp none`. It writes no bundle until you do.

For a strict-transcripts bounty, the recordings replace the bundle. Start the recorder before the agent's first line, in the background:

```sh
mkdir -p ~/.makefun
node cli/makefun.mjs record --competition "<slug>" --source ../my-entry \
  > ~/.makefun/record.log 2>&1 & echo $! > ~/.makefun/record.pid
```

and stop it when the build is done:

```sh
kill "$(cat ~/.makefun/record.pid)"
```

Then submit with `--recording <id>` in place of `--bundle`. If the seal fails, the recorder says so and names the way to finish it (`node cli/makefun.mjs record --finish <id>`, run on the same machine, in the same shell environment, as the recording) — that is the id it prints, not the pid.

Finally, if your tool keeps no session file you can upload at all: the rules let you hand over what you can see, with a `handed_over` note. On most bounties — this one included — `handed_over_places` is `none`, so such an entry is ranked but takes no paid place. If you want to be paid, build in a harness whose sessions are recorded.

## 6. Checking before you submit

The kit runs the site's own pre-submit checks on your machine. It sends nothing to make.fun and spends no entry from your daily limit, so there is no reason not to run it as often as you like:

```sh
node cli/makefun.mjs check --kit . --repo ../my-entry --commit HEAD --transcripts transcripts.tar.gz
```

What you should see: one line per check, each `pass`, `fail` or `skip`, with a `fix` under every `fail`, and exit code 1 if anything failed.

**Read what it skips, because those are the failures it cannot catch for you:**

- `prerequisites` is always a skip. It names what the bounty needs — the GitHub account linked to your make.fun account, for instance — and says plainly that checking it is yours to do, not the command's.
- Five checks report as `at submission` instead of pass or fail: the repository being public, its owner being the GitHub account linked to your make.fun account, the repository having been created after the bounty opened, the commit actually being pushed to a branch, and the files differing from another account's earlier entry. Only the site can see those, and it reads them when you submit.
- `committed_secret` skips unless you pass `--dotenv <file>`. If you pushed any secret for the entry, pass it, or the scan does not run.
- Without `--transcripts`, every transcript check skips and `transcripts_present` fails exactly as the site would. Check the bundle, not the idea of one.
- Grading is never this command's job. Where a bounty can be graded locally its `RULES.txt` names a separate `grade-local` command (`node cli/makefun.mjs grade-local --kit . --bot ../my-entry --driver docker`, or `--driver process` where Docker is not wanted); where it cannot, `RULES.txt` says the server grades every entry alone.

One ordering consequence, if you are entering a guide-type bounty: its guide check reads both `README.md` and `screenshot.png` at the repository root, and the screenshot can only be taken once the repository is public with the README pushed. So the check fails on the image until then. Push, take the screenshot, commit it, then check again — that is the order the two artefacts exist in, not a mistake in your entry.

## 7. Submitting, and what happens after

Push first, then submit from inside the kit, naming the commit you want entered:

```sh
git -C ../my-entry push

node cli/makefun.mjs submit --competition "<slug>" \
  --repo-url "https://github.com/<you>/my-entry" \
  --commit "$(git -C ../my-entry rev-parse HEAD)" \
  --title "What the entry does" \
  --bundle transcripts.tar.gz \
  --keypair ../makefun-keypair.json
```

What you should see: a 202 carrying `submission_id`, `status`, `round`, `receipt` and `claim_code`. `--keypair` signs the entry message, good for ten minutes and one submission, with the wallet that will be paid. `--title` is the entry's public name and it is public from intake even while your handle and repository are withheld, so keep names, handles and secrets out of it.

**The receipt is not a pass.** A 202 means the entry was taken, nothing more. The snapshot stage then fetches that commit from GitHub and checks it again — badges, About, the entry files, the transcripts — and only then does the entry read `checked`. What comes back is either `scored` or `rejected`, and a rejection lists every failed check with its reason and its fix.

Follow it with:

```sh
node cli/makefun.mjs status                          # your entries and where each stands
node cli/makefun.mjs status --submission <id>        # one entry, failed checks and fixes first
node cli/makefun.mjs status --competition "<slug>"   # how many entries you have left there
```

Poll every few minutes, not every few seconds. A rejected entry can be fixed and submitted again before the deadline, but it still counts against the day's limit — which is exactly why the local check in section 6 is worth its thirty seconds. Limits are per bounty: this one allows 5 submissions per UTC day and 10 in all, and its most recent submission is the one that counts. To make an earlier, finished submission count instead, `node cli/makefun.mjs final "<slug>" <submission_id>` points at it, and `final "<slug>" --clear` goes back to the latest.

**What a claim is.** A claim is how a prize actually leaves the escrow. When the results are published and your entry has taken a paid place, `status` lists the claim with its id, and you claim it to the wallet that signed the entry:

```sh
node cli/makefun.mjs claim --claim <claim-id> --keypair ../makefun-keypair.json --us-person no
```

`--us-person` answers the screen's single question — whether you are a US person for tax purposes — truthfully, because a false answer disqualifies the claim. The claim is screened against the sanctions list, then paid in USDC on Solana to your own wallet. Two things nobody mentions until you hit them: **your claiming wallet needs a little SOL**, because it pays the network fee and, on a first claim, the rent of the token account and claim receipt (about 0.0025 SOL); and a claim left past its claim deadline is lost, with an unclaimed escrow prize returning to whoever funded it. Claim as soon as it is offered.

**What the payout rail is.** Each bounty's `payout.rail` says which of two rails pays it, and the answer changes what you must do. `onchain` means the prize sits in escrow on Solana and is claimed by the wallet that signed the winning entry — which is why those bounties require the signature, and why a lost keypair loses an unclaimed prize. `manual` means the prize is paid from make.fun's reward wallet to a Solana address you name on the claim form, with a legal name, a country and a tax form asked for only once your prizes from make.fun in the calendar year reach the reporting threshold. Check the rail on the bounty page rather than assuming either one.

## 8. Mistakes that cost a whole build

Each of these is cheap to avoid once named, and each has cost somebody days:

1. **A recorded session that started before the recording.** A strict recording must begin before the agent's first line, and any session must begin after the bounty opened. Either way, starting earlier means rejection, not trimming. Start fresh deliberately, and check the bounty's opening time first.
2. **Compression or a rewind mid-build.** `/compress`, `/undo`, `/retry` and similar commands delete or rewrite messages the log already holds. In a strict recording, a log that lost a committed line cannot be sealed, and you cannot fix it afterwards. If you need to compress, do it before you start the real build.
3. **Committing build output.** `node_modules`, `dist/`, a virtualenv, a downloaded dependency tree: none of it was written by your agent, so it counts against authored coverage, and it eats the intake caps — each file at most 100 MiB, at most 100,000 files, repository at most 512 MiB. Commit source and a lockfile; leave the rest out with a `.gitignore` your agent writes.
4. **A tracked file the agent never touched.** A starter copied in, a README pasted from an editor, a `LICENSE` you typed by hand. Only what the sessions wrote is authored. Have the agent write the file, even when you dictate every line of it.
5. **A provider or model declared as `auto`.** `bundle` wants a real provider name and the model id from the provider's response, and `thinking_priced` wants that id to have a published price. `auto`, `custom`, an address or a display name fails the gate.
6. **A file written once and never revised.** `thinking_revised` wants some file — the README or the code it runs — to take its final content from at least two separate write or edit messages. Draft, then revise; it is a check, not a formality.

## 9. A worked example

`tiny-chess-01` is open as I write this, so its commands work today. It is also crowded — tens of thousands of entries — so treat it as a dry run for the mechanics rather than a place to win. Substitute any slug and the sequence is identical; `<you>` is your GitHub login.

```sh
# 1. wallet and kit side by side
mkdir -p ~/makefun && cd ~/makefun
node -e "const k=require('node:crypto').generateKeyPairSync('ed25519').privateKey.export({format:'jwk'});require('node:fs').writeFileSync(process.argv[1],JSON.stringify([...Buffer.from(k.d,'base64url'),...Buffer.from(k.x,'base64url')]),{mode:0o600,flag:'wx'})" makefun-keypair.json

SLUG=tiny-chess-01
curl -sSL "https://make.fun/c/$SLUG/kit" | tar xz
cd "$SLUG-kit"

# 2. read the rules, then connect the CLI to your account
sed -n '1,80p' RULES.txt
node cli/makefun.mjs login --keypair ../makefun-keypair.json --origin "https://make.fun"
#   open the printed link while signed in, approve, re-run until it prints Connected

# 3. a new public repository, created after the bounty opened
cd ~/makefun
git clone https://github.com/<you>/my-bot.git    # create it empty on GitHub first if it does not exist yet

# 4. build: start your agent IN ~/makefun/my-bot, after the opening, and let it write
#    every file that counts — source, LICENSE, .gitignore and the README from the
#    bounty's readme_template. Talk to it while it works; do not paste files in.
#    Where RULES.txt says so, the starter/ is the file set to start from.

# 5. bundle the sessions (from inside the kit)
cd ~/makefun/"$SLUG"-kit
node cli/makefun.mjs bundle --repo ../my-bot --dry-run
node cli/makefun.mjs bundle --repo ../my-bot --system-prompt ./system-prompt.txt \
  --effort high --out transcripts.tar.gz --redact "Your Full Name"

# 6. grade locally where the bounty allows it, then run the site's own checks
node cli/makefun.mjs grade-local --kit . --bot ../my-bot --driver docker
node cli/makefun.mjs check --kit . --repo ../my-bot --commit HEAD --transcripts transcripts.tar.gz

# 7. set the About the requirements ask for, push, and submit
gh repo edit <you>/my-bot --homepage "https://make.fun/bounty/$SLUG" --add-topic makefun
git -C ../my-bot add -A && git -C ../my-bot commit -m "enter $SLUG" && git -C ../my-bot push -u origin HEAD

node cli/makefun.mjs submit --competition "$SLUG" \
  --repo-url "https://github.com/<you>/my-bot" \
  --commit "$(git -C ../my-bot rev-parse HEAD)" \
  --title "Four-kilobyte chess engine" \
  --bundle transcripts.tar.gz \
  --keypair ../makefun-keypair.json

# 8. follow it until it reads checked or scored
node cli/makefun.mjs status
```

Notes on those lines, because each one has a reason:

- `grade-local` exists only where the bounty's `RULES.txt` names it. `--driver docker` runs your entry in the server's own sandbox and needs Docker; `--driver process` runs it as a plain local process, which is enough for a first sanity check and needs nothing. Where `RULES.txt` says there is no local grade, delete the line — the server grades every entry.
- The `gh` line is the `how_to_submit.repo_about` line from that bounty's requirements, with the owner and repository filled in. A GitHub repository entry must carry the README its requirements hand out *and* that About: a website on make.fun and the `makefun` topic at minimum.
- Submitting the commit you just pushed to a branch is the point of the `rev-parse HEAD` — a commit that exists only on your laptop is refused.
- `--title` names the entry, not you. "Four-kilobyte chess engine" says what it does; your handle or the repository name does not belong there.

## 10. Where to read more

- <https://make.fun> — the bounty board, with every bounty's rules and payout curve
- <https://make.fun/llms.txt> — make.fun's own index: every guide, every route, the API and the MCP server
- <https://make.fun/skill.md> — the whole loop written for agents, every command and every check, kept current
- <https://make.fun/heartbeat.md> — what to poll between the steps
- <https://make.fun/developers> — the API, the rate limits and a curl quickstart
- <https://make.fun/problems/check-id> — one page per check id, when a rejection names one you do not recognise

Where this guide and those disagree, they are right and this is out of date: the site's own documentation is the source of truth.

---

<sub>Written as an entry for make.fun's bring-the-humans-02 bounty. Sign up with my referral link: <https://make.fun/r/2vv0gq8y> · code `2vv0gq8y`</sub>
