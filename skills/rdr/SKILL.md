---
name: rdr
description: Recall, then research, then decide. Use before a strategic or hard-to-reverse choice, or when the user asks "what did we already decide about X", wants a deep-research prompt that skips what is already known, or wants a decision memo scaffold. Searches the local TurnState ledger and optional notes; no LLM, no network.
---

# RDR: recall, research, decide

RDR is a three-step loop backed by `modules/rdr/rdr.py` (Python 3 standard library only). It reads
the TurnState SQLite ledger that this plugin's Stop hook fills, so recall works on past sessions.

Run the script with the plugin root that Claude Code provides:

```bash
RDR="${CLAUDE_PLUGIN_ROOT}/modules/rdr/rdr.py"
```

## Steps, in order

1. **Recall.** See what past sessions already said about the question.

   ```bash
   python3 "$RDR" recall "<question>"
   ```

   Read the hits before doing anything else. If they already answer the question, say so and stop.

2. **Research.** Print a deep-research prompt with the recall hits injected as context, so the
   research covers only the gaps.

   ```bash
   python3 "$RDR" research "<question>"
   ```

   This only prints text. Give it to the user, or run it in a research tool only if the user asks.

3. **Memo.** Create a decision memo scaffold to fill with recall, research, options, risks and the
   decision.

   ```bash
   python3 "$RDR" memo "<topic>"
   ```

   It writes a new file under `CHARMOS_MEMO_DIR` (default `./decisions`) and never overwrites an
   existing memo. Tell the user the path it printed.

## Configuration (environment variables, optional)

| variable | default | meaning |
|---|---|---|
| `CHARMOS_TURNSTATE_DB` | `~/.charmos/turnstate/turnstate.db` | ledger to recall from |
| `CHARMOS_NOTES_DIR` | unset | extra folder of `.md`/`.txt` notes searched by recall |
| `CHARMOS_MEMO_DIR` | `./decisions` | where `memo` writes |

## Notes

- Recall is whole-word term overlap, not semantic search. Try a second phrasing before concluding
  that nothing was recorded.
- An empty ledger usually means the Stop hook has not run yet, or the ledger lives at a different
  `CHARMOS_TURNSTATE_DB` path. Say which one you checked.
- `recall` reads every `.md`/`.txt` file under `CHARMOS_NOTES_DIR` recursively; point it only at a
  folder the user intends.
