# CharmOS plugin for Claude Code

One hook and two skills, all deterministic Python 3 standard library code. No LLM calls, no
network access, no third-party packages.

## Install

```
/plugin marketplace add tonydzi/charm-os
/plugin install charm-os@charm-os
```

Requires `python3` on `PATH`.

## What the hook stores: read this first

**The TurnState Stop hook writes your prompts into a local SQLite database.** After every turn it
appends one row to `~/.charmos/turnstate/turnstate.db` (or the path in `CHARMOS_TURNSTATE_DB`)
containing:

- your prompt for that turn (first 500 characters),
- the assistant's reply text (first 1200 characters),
- files written or edited, tools used, shell commands run (each command clipped to 200 characters),
- lines that look like decisions or TODOs,
- the working directory (cwd) and its folder name, used as the project name (a full path can
  contain your OS username or a client or project name),
- the session id and a pointer to the transcript file.

If that folder cannot be created, the database falls back to the system temp folder. The hook also
keeps one small byte-offset file per session in the system temp folder
(`charmos-turnstate-<session>.off`, a number only). The data stays on your
machine and is never sent anywhere, but anything you type, including secrets pasted into a prompt
or a shell command, can end up in that file. Treat it like your session transcripts.

To stop collecting, disable or uninstall the plugin. To erase what was collected, delete the
`~/.charmos/turnstate/` folder (or the file at `CHARMOS_TURNSTATE_DB`).

The hook never prints and never blocks a turn; on any error it exits 0. If it misses turns, the
companion `modules/turnstate/turnstate_backfill.py` rebuilds the ledger from transcripts
(`--check` reports gaps).

## Skills

| skill | use it for |
|---|---|
| `rdr` | Recall what past sessions already said, print a deep-research prompt for the gaps, scaffold a decision memo. Reads the TurnState ledger. |
| `agent-trace-eval` | Score a multi-agent JSONL event trace against four safety invariants; exit code = failed checks. |

## Configuration (environment variables, optional)

| variable | default | used by |
|---|---|---|
| `CHARMOS_TURNSTATE_DB` | `~/.charmos/turnstate/turnstate.db` | hook, `rdr` |
| `CHARMOS_NOTES_DIR` | unset | `rdr recall` |
| `CHARMOS_MEMO_DIR` | `./decisions` | `rdr memo` |

## Layout

The repository root is the plugin: `.claude-plugin/plugin.json`, `hooks/hooks.json` and `skills/`
sit next to `modules/`, so the hook runs the same `modules/turnstate/turnstate_hook.py` that is
documented and tested there. No symlinks, nothing outside the plugin root.

License: Apache-2.0. Privacy: [PRIVACY.md](https://github.com/tonydzi/charm-os/blob/main/PRIVACY.md).
