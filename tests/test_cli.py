import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from ghsecret.cli import build_parser, main


class CliTests(unittest.TestCase):
    def test_help(self):
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                build_parser().parse_args(["scan", "--help"])
        self.assertEqual(raised.exception.code, 0)

    def test_clean_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("Hallo Welt\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["scan", str(root)]), 0)

    def test_json_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            secret = "abcdefghijklmnopqrstuvwxyz123456"
            (root / "config.env").write_text(f"API_KEY={secret}\n", encoding="utf-8")
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                self.assertEqual(main(["scan", str(root), "--format", "json"]), 1)
            payload = json.loads(stream.getvalue())
            self.assertEqual(payload["treffer"], 1)
            self.assertNotIn(secret, stream.getvalue())

    def test_missing_target(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["scan", "/definitely/not/a/repository"]), 2)


if __name__ == "__main__":
    unittest.main()
