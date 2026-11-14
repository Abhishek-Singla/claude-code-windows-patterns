import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FP = ROOT / "examples" / "fingerprint" / "fingerprint.py"
VM = ROOT / "examples" / "markers" / "verify_marker.py"
SCAN = ROOT / "examples" / "routine-mirror" / "secret_scan.py"


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)


class FingerprintTests(unittest.TestCase):
    def test_skip_when_unchanged_rebuild_when_changed(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "a.txt").write_text("one")
            args = ["--state", d / "s.json", "--files", str(d / "*.txt")]
            self.assertEqual(run(FP, "check", *args).returncode, 1)  # no state yet
            run(FP, "update", *args)
            self.assertEqual(run(FP, "check", *args).returncode, 0)  # unchanged: skip
            (d / "b.txt").write_text("new file")
            self.assertEqual(run(FP, "check", *args).returncode, 1)  # added: rebuild
            run(FP, "update", *args)
            (d / "a.txt").write_text("one!")
            self.assertEqual(run(FP, "check", *args).returncode, 1)  # modified: rebuild

    def test_hash_mode_detects_same_size_edit(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            f = d / "a.txt"
            f.write_text("abc")
            args = ["--state", d / "s.json", "--files", str(d / "*.txt"), "--hash"]
            run(FP, "update", *args)
            f.write_text("abd")
            self.assertEqual(run(FP, "check", *args).returncode, 1)


class MarkerTests(unittest.TestCase):
    def test_marker_written_then_cleared(self):
        with tempfile.TemporaryDirectory() as d:
            marker = Path(d) / "VERIFY_FAILED.txt"
            r = run(VM, "--dir", d, "--", sys.executable, "-c", "print('bad total'); raise SystemExit(3)")
            self.assertEqual(r.returncode, 1)
            self.assertIn("bad total", marker.read_text())
            r = run(VM, "--dir", d, "--", sys.executable, "-c", "pass")
            self.assertEqual(r.returncode, 0)
            self.assertFalse(marker.exists())


class ScanTests(unittest.TestCase):
    def test_clean_and_dirty(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "ok.ps1").write_text("Write-Host 'hello'\n")
            self.assertEqual(run(SCAN, d).returncode, 0)
            profile_path = "C:" + "\\" + "Users" + "\\" + "someone"  # built in parts so this file passes its own scan
            (d / "bad.ps1").write_text(f"$p = '{profile_path}'\n")
            (d / "data.csv").write_text("a,b\n")
            r = run(SCAN, d)
            self.assertEqual(r.returncode, 1)
            self.assertIn("user-profile path", r.stdout)
            self.assertIn("file type must not be mirrored", r.stdout)


if __name__ == "__main__":
    unittest.main()
