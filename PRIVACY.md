# Privacy policy: CharmOS Claude Code plugin

The CharmOS plugin sends no data anywhere. It makes no network requests and has no telemetry.

## What it stores locally

The TurnState Stop hook writes your prompts into a local SQLite database. After each turn it
stores, on your own machine, at `~/.charmos/turnstate/turnstate.db` (or `CHARMOS_TURNSTATE_DB`):
your prompt (clipped to 500 characters), the assistant's reply text (clipped to 1200 characters),
names of files written or edited, tools used, shell commands run, decision-like lines, the session
id and the transcript path. Anything you type, including secrets in a prompt or command, can be
stored there. If that folder cannot be created, the database is placed in the system temp folder.
The hook also keeps one per-session byte-offset file (a number only) in the system temp folder.

The `rdr` skill reads that database and, if you set `CHARMOS_NOTES_DIR`, the notes in that folder.
`rdr memo` writes memo files to `CHARMOS_MEMO_DIR` (default `./decisions`). The `agent-trace-eval`
skill reads the trace file you give it and writes a scorecard only if you pass `--json`.

## Control

Disable or uninstall the plugin to stop collection. Delete `~/.charmos/turnstate/` (or the file at
`CHARMOS_TURNSTATE_DB`) to erase what was stored.

For the repository's wider data rules, see [docs/privacy.md](docs/privacy.md).
