"""Regression for charm-os#3: a tail the hook skips (over MAX_NEW_BYTES) must still be backfilled.

Scenario: a resumed session's first hook call sees a >4 MB tail and skips it; the next turn writes a
normal row. The backfill must then ingest the skipped stretch (rows starting at byte 0), and the
freshness gate must not report FRESH while the gap is open.
Run: python3 -m unittest modules/turnstate/test_gap_backfill.py  (stdlib only)
"""
import json, os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "turnstate_hook.py")
BACKFILL = os.path.join(HERE, "turnstate_backfill.py")


def turn(i, pad=""):
    u = {"type": "user", "timestamp": "2026-11-0%dT10:00:00Z" % (1 + i % 5),
         "message": {"role": "user", "content": "ask number %d %s" % (i, pad)}}
    a = {"type": "assistant", "timestamp": "2026-11-0%dT10:00:01Z" % (1 + i % 5),
         "message": {"role": "assistant", "content": [{"type": "text", "text": "answer %d" % i}]}}
    return (json.dumps(u) + "\n" + json.dumps(a) + "\n").encode()


class GapBackfill(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.sid = "gaptest-%d" % os.getpid()
        self.tpath = os.path.join(self.tmp, self.sid + ".jsonl")
        self.env = dict(os.environ, CHARMOS_TURNSTATE_DB=os.path.join(self.tmp, "ts", "ledger.db"),
                        CHARMOS_TRANSCRIPTS_GLOB=os.path.join(self.tmp, "*.jsonl"),
                        TMPDIR=self.tmp)

    def hook(self):
        payload = json.dumps({"session_id": self.sid, "transcript_path": self.tpath, "cwd": self.tmp})
        subprocess.run([sys.executable, HOOK], input=payload.encode(), env=self.env, check=True)

    def run_bf(self, *args):
        return subprocess.run([sys.executable, BACKFILL, *args], env=self.env,
                              capture_output=True, text=True)

    def test_skipped_tail_is_backfilled(self):
        with open(self.tpath, "wb") as f:
            for i in range(60):                       # ~6 MB of turns, all before the first hook call
                f.write(turn(i, "x" * 100000))
        self.hook()                                   # skips the >4 MB tail
        with open(self.tpath, "ab") as f:
            f.write(turn(99))                         # the next normal turn
        self.hook()                                   # must not move coverage past the skipped stretch
        os.utime(self.tpath, (1, 1))                  # make it a "finished" session for --check
        self.assertEqual(self.run_bf("--check").returncode, 2, "gap open -> must report STALE")
        self.run_bf()                                 # nightly backfill
        import sqlite3
        con = sqlite3.connect(self.env["CHARMOS_TURNSTATE_DB"])
        first = con.execute("SELECT MIN(byte_start) FROM turns WHERE session_id=?", (self.sid,)).fetchone()[0]
        n = con.execute("SELECT COUNT(*) FROM turns WHERE session_id=?", (self.sid,)).fetchone()[0]
        self.assertEqual(first, 0, "skipped stretch was never ingested")
        self.assertGreaterEqual(n, 60)
        self.assertEqual(self.run_bf("--check").returncode, 0)


if __name__ == "__main__":
    unittest.main()
