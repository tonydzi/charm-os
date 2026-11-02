"""Regression for charm-os#4: bad input degrades visibly, never silently and never by crashing.

1. sanitize.py counts malformed lines and prints malformed=N.
2. eval.load() skips-and-counts a parseable event that lacks "type"/"ts" (or is not an object),
   so the invariants that index e["type"] / e["ts"] cannot KeyError.
Run: python3 -m unittest modules/eval-harness/test_degrade_visibly.py  (stdlib only)
"""
import json, os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eval as ev  # noqa: E402


class DegradeVisibly(unittest.TestCase):
    def test_sanitize_counts_malformed(self):
        d = tempfile.mkdtemp()
        good = {"event_id": "e1", "proposal_id": "p1", "type": "COMMIT", "ts": "2026-11-01T00:00:00Z", "actor": "a"}
        with open(os.path.join(d, "log-1.jsonl"), "w") as f:
            f.write(json.dumps(good) + "\n" + '{"type": "COMMI')   # half-written last line
        out = os.path.join(d, "out.jsonl")
        r = subprocess.run([sys.executable, os.path.join(HERE, "sanitize.py"), d, out],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("malformed=1", r.stdout)

    def test_load_skips_event_without_type_or_ts(self):
        p = os.path.join(tempfile.mkdtemp(), "t.jsonl")
        rows = [{"proposal_id": "p1", "type": "COMMIT", "ts": "2026-11-01T00:00:00Z"},
                {"proposal_id": "p1", "ts": "2026-11-01T00:00:01Z"},          # no type
                {"proposal_id": "p1", "type": "ESCALATE"},                     # no ts
                [1, 2, 3]]                                                      # not an object
        with open(p, "w") as f:
            f.write("\n".join(json.dumps(r) for r in rows) + "\n")
        by_prop, n, skipped = ev.load(p)
        self.assertEqual((n, skipped), (1, 3))
        from invariants import INVARIANTS
        for _name, inv in INVARIANTS:               # must not raise
            inv(by_prop["p1"])


if __name__ == "__main__":
    unittest.main()
