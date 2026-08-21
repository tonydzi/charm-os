#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""to_agentevals.py - run a tracekit trace through LangChain's AgentEvals and show what it sees.

WHY THIS FILE EXISTS
    Same reason as to_invariant.py: an engineer named AgentEvals in the Habr thread, so the
    honest reply is a run, not an opinion. AgentEvals asks a different question than we do -
    "did this trajectory match a reference trajectory?" rather than "did this trajectory break
    a rule" - and this script makes that difference measurable instead of arguable.

WHAT IT DOES
    PART 1 - scores all proposals against a reference built from one clean proposal, in all four
             deterministic match modes (strict / unordered / subset / superset).
    PART 2 - the order probe. Reference: PROPOSE, HUMAN_APPROVED, COMMIT. Output: the same three
             events with the human approval AFTER the commit, i.e. exactly the defect INV-1
             exists to catch. Prints which modes see it.
    PART 3 - the length probe: one extra harmless event added to an otherwise perfect trajectory.

    The LLM-as-judge evaluator is deliberately NOT run here: it needs an API key and it is
    non-deterministic (measured: 0.3 / 0.42 / 0.58 on three runs over one identical trace),
    which is the opposite of what a benchmark needs. See ../interop/README.md for that run.

INPUT / OUTPUT
    in : path to a tracekit JSONL trace (default: the public-live-v0 fixture)
    out: three tables. No exit-code gate - this script reports what the tool can and cannot see.

REQUIRES
    pip install agentevals   (tested against 0.0.9; pulls langchain-core + openevals)

CALLED BY
    a human, or CI. Nothing in the harness imports it - the harness stays dependency-free.
    rail: none for the deterministic matchers (0 tokens, 0 network).
    updated: 2026-08-21
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TRACE = os.path.join(HERE, "..", "benchmarks", "public-live-v0", "fixture.jsonl")
MODES = ["strict", "unordered", "subset", "superset"]


def load(path):
    by = collections.defaultdict(list)
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                e = json.loads(ln)
            except json.JSONDecodeError:
                continue
            by[e.get("proposal_id")].append(e)
    return by


def adapt(events):
    """tracekit events -> OpenAI-shaped messages. AgentEvals compares TOOL CALLS, so each trace
    event becomes one tool call named after the event type; the actor rides in the arguments."""
    ev = sorted(events, key=lambda e: e.get("ts", ""))
    return [{"role": "assistant", "content": "", "tool_calls": [{
        "id": e.get("event_id", ""), "type": "function",
        "function": {"name": e["type"],
                     "arguments": json.dumps({"actor": e.get("actor", "")})}}]} for e in ev]


def _tc(name, actor="a"):
    return {"role": "assistant", "content": "", "tool_calls": [{
        "id": name + "-" + actor, "type": "function",
        "function": {"name": name, "arguments": json.dumps({"actor": actor})}}]}


def _ours(events):
    sys.path.insert(0, os.path.join(HERE, ".."))
    from invariants import INVARIANTS
    fails = [n.split()[0] for n, fn in INVARIANTS if fn(events).status == "fail"]
    return ",".join(fails) if fails else "clean"


def main():
    try:
        from agentevals.trajectory.match import create_trajectory_match_evaluator
    except ImportError:
        print("  agentevals is not installed: pip install agentevals", file=sys.stderr)
        return 2

    ev = {m: create_trajectory_match_evaluator(trajectory_match_mode=m,
                                               tool_args_match_mode="ignore") for m in MODES}
    path = next((a for a in sys.argv[1:] if not a.startswith("--")), DEFAULT_TRACE)
    by = load(path)
    if not by:
        print("  no readable events in %s - empty or malformed trace" % path, file=sys.stderr)
        return 2

    # the reference is the proposal our own harness scores clean - the closest thing a live
    # fleet has to an "ideal trajectory", since nobody hand-writes reference runs for it.
    clean = sorted(by, key=lambda p: (_ours(by[p]) != "clean", p))[0]
    reference = adapt(by[clean])

    print("\n  PART 1 - fixture vs reference = the clean proposal %s (%d events)\n"
          % (clean[:12], len(reference)))
    print("  %-14s %-12s %s" % ("proposal", "ours", " ".join("%-10s" % m for m in MODES)))
    for pid, events in sorted(by.items()):
        out = adapt(events)
        row = [str(ev[m](outputs=out, reference_outputs=reference)["score"]) for m in MODES]
        print("  %-14s %-12s %s" % (pid[:12], _ours(events), " ".join("%-10s" % v for v in row)))

    print("\n  PART 2 - can the matchers see the order defect INV-1 exists to catch?")
    print("  reference: PROPOSE, HUMAN_APPROVED, COMMIT   (human gate honoured)")
    print("  output   : PROPOSE, COMMIT, HUMAN_APPROVED   (committed BEFORE approval)\n")
    ref = [_tc("PROPOSE"), _tc("HUMAN_APPROVED", "anton"), _tc("COMMIT")]
    bad = [_tc("PROPOSE"), _tc("COMMIT"), _tc("HUMAN_APPROVED", "anton")]
    for m in MODES:
        s = ev[m](outputs=bad, reference_outputs=ref)["score"]
        print("    %-10s score=%-6s %s" % (
            m, s, "catches it" if s is False else "MISSES it - scores the defect as a match"))

    print("\n  PART 3 - one extra harmless event (real fleet traces are never fixed-length)\n")
    extra = [_tc("PROPOSE"), _tc("HUMAN_APPROVED", "anton"), _tc("CLARIFY"), _tc("COMMIT")]
    for m in MODES:
        print("    %-10s score=%s" % (m, ev[m](outputs=extra, reference_outputs=ref)["score"]))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
