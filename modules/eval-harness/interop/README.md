# interop/ - this harness measured against Invariant Guardrails and AgentEvals

An engineer reading our benchmark write-up named two existing tools and asked the fair question:
what do they already do that this does? Prose would be cheap, so this directory answers in code.
Both scripts run our **published** fixture (`../benchmarks/public-live-v0/fixture.jsonl`,
4 proposals / 24 events) through the other tool and print the verdicts side by side.

```
pip install invariant-ai agentevals
python to_invariant.py     # exit code = disagreements + failed controls
python to_agentevals.py
```

Versions measured, 2026-08-21: `invariant-ai` 0.3.5 (repo HEAD `2340fe2`, last push 2026-01-12,
446 stars, 10 open issues) · `agentevals` 0.0.9 (repo HEAD `946ad15`, last push 2026-07-14,
704 stars, 24 open issues).

## Result 1 - Invariant Guardrails expresses all four of our invariants, and agrees on every verdict

INV-1..INV-4 were rewritten as `raise ... if:` rules in Invariant's own language (they are in
`to_invariant.py`, not paraphrased here). Over the fixture: **16 of 16 verdicts agree, 0
disagreements.** 14 of 14 red/green controls behave (a rule that never fires cannot pass itself
off as agreement), and mutating the fixture - stripping every `HUMAN_APPROVED` event - flips both
engines to violation together.

So the honest headline is not "we found a gap". It is: **a general-purpose guardrail language
already covers what our four hand-written Python functions cover.** Our invariants are not a
capability nobody had; they are a specific, opinionated *choice* of four rules plus a scorecard.

What that cost, measured rather than guessed:

| | this harness | Invariant Guardrails |
|---|---|---|
| lines you must trust | 232 (`eval.py` + `invariants.py`) | a parser, type checker, optimizer and async interpreter |
| dependencies | none - Python stdlib | 76 packages / 127 MB in a clean venv |
| network by default | none | **the default `Policy` uploads your trace** to `explorer.invariantlabs.ai`; you must ask for `LocalPolicy` to stay offline |
| runtime on the fixture | 0.07 s | seconds, and it hit its own limit (below) |
| verdict vocabulary | pass / fail / **n/a** + pass-rate + exit code | violation / no violation |

Two things found in their code while doing this, reported here rather than as drive-by issues
(that repo has had no push since January, so a cold PR would sit in a silent queue):

1. **Default evaluation budget is too small for nested quantifiers.** A rule of the shape
   "commit exists AND `count(max=0)` of the approving pattern" blows
   `Maximum checking cycles exceeded: 100` on an **8-event** trace. Real agent traces are longer
   than eight events. Workaround: `INVARIANT_MAX_ITERATIONS`.
2. **`EvaluationContext(maximum_iterations=...)` is dead code.** The constructor accepts the
   argument and then overwrites it with `int(os.environ.get("INVARIANT_MAX_ITERATIONS", 100))`,
   so a caller passing it silently gets 100 anyway
   (`invariant/analyzer/runtime/evaluation_context.py:25-30`).

One trap worth flagging for anyone else writing rules in that language, because we fell into it.
"This commit was approved" has to be written as an absence check, `count(max=0)` over the
approving pattern - and the block inside a quantifier binds its own fresh variables. Write it the
obvious way and the rule silently asks *"does any approved commit exist anywhere in this trace"*
instead of *"was this commit approved"*, so a trace with an unapproved commit followed by an
approved one comes back clean. Our first draft did exactly that; it agreed with our harness on the
fixture (one commit per proposal) and would have been wrong the moment a proposal committed twice.
The fix is one line - `c2.id == c.id` inside the inner block - and the "two commits, first
unapproved" control keeps it fixed. An adversarial review found it, not our green run.

Where Invariant is plainly ahead of us, and we are not going to pretend otherwise: it enforces at
runtime as an LLM/MCP proxy instead of scoring after the fact; it ships content detectors we have
none of (PII, secrets, prompt injection, moderation, code, copyright, OCR); it localises a
violation to the exact span of text; and it has an incremental `Monitor` that checks *pending*
events before they execute.

## Result 2 - AgentEvals answers a different question, and three of its four modes miss our defect

AgentEvals is reference-based: "did this trajectory match a reference trajectory?" That is a real
question, but not ours - a live autonomous fleet has no hand-written reference run to compare
against, which is exactly why we score against rules instead.

Scoring the fixture against a reference built from the one proposal we score clean:

```
proposal       ours         strict     unordered  subset     superset
5bc42bac1c18   INV-2 fail   False      True       True       True
d3207790fddc   INV-2 fail   False      False      False      False
e53fd7fe8845   INV-2 fail   False      False      False      True
f7c96ed9e1a7   clean        True       True       True       True
```

Row 1 is the interesting one. Proposal `5bc42bac` and the clean reference contain the *same
multiset of tool calls* (PROPOSE, ACCEPT, COMMIT, VERIFY, VERIFY) - so `unordered` calls them a
match, while our INV-2 fails it, because in one of them the only verifier before the commit is
the committer itself. Order and actor identity are the whole difference, and the multiset modes
discard both.

Made explicit with a minimal case (PART 2 of `to_agentevals.py`) - reference
`PROPOSE, HUMAN_APPROVED, COMMIT` versus an output that commits *before* the human approves:

```
strict     score=False  catches it
unordered  score=True   MISSES it - scores the defect as a match
subset     score=True   MISSES it
superset   score=True   MISSES it
```

`strict` does catch it - and `strict` also returns `False` when a single harmless extra event
appears in the trace (PART 3), which every real fleet trace has. That is the bind: the one mode
that sees the ordering defect is too brittle for live traces, and the modes that tolerate live
traces cannot see the defect. Either way the answer is one boolean for the whole trajectory, with
no statement of *which* rule broke.

We also ran their reference-free **LLM-as-judge** on the same four proposals
(`openai/gpt-5.6-terra-pro` via OpenRouter, `continuous=True`):

```
5bc42bac1c18  ours=INV-2 fail   judge=0.58
d3207790fddc  ours=INV-2 fail   judge=0.86
e53fd7fe8845  ours=INV-2 fail   judge=0.76
f7c96ed9e1a7  ours=clean        judge=0.78

same proposal judged three times: 0.3 / 0.42 / 0.58
```

It scored a rule-violating trace (0.86) above the clean one (0.78), and moved 0.28 on identical
input across three runs. This is not a gotcha - that judge grades trajectory *coherence* against
a generic rubric, not our invariants, and it was never asked about human gates. It is the reason
the deterministic checks exist alongside it: a number that moves when the input does not cannot
be a regression gate. That script is not committed here because it needs an API key and produces
a different answer every run.

Where AgentEvals is ahead of us: four tool-argument match modes with per-tool overrides, first
class LangGraph thread/snapshot extraction, async everywhere, JS/TS parity, LangSmith wiring, and
few-shot examples for the judge. If you *do* have reference trajectories, it does that job and we
do not do it at all.

## What this leaves as actually ours

Not the idea of checking agent traces against rules - that existed. What is ours after this run:

- a **published live fixture plus a committed scorecard**, so anyone can rerun the exact numbers;
  neither tool ships fleet-behaviour benchmark data;
- **`n/a` as a first-class verdict** (this invariant does not apply to this proposal), which keeps
  the denominator honest - both other tools have only true/false;
- **zero dependencies, zero network, 0.07 s, exit code = failed checks**, which is what makes it
  a CI gate rather than a service;
- and the four rules themselves, stated in the open in 115 lines you can disagree with and edit.

Everything above is reproducible from this directory. If a number here is wrong, the script that
produced it is right next to it.
