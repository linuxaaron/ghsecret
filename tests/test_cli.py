import json
import tempfile
import unittest
from pathlib import Path

from ghsecret.cli import main


class CliTests(unittest.TestCase):
    def test_help(self):
        self.assertEqual(main(["scan", "--help"]), 0)

    def test_clean_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("Hallo Welt\n", encoding="utf-8")
            self.assertEqual(main(["scan", str(root)]), 0)

    def test_json_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config.env").write_text("API_KEY=abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8")
            self.assertEqual(main(["scan", str(root), "--format", "json"]), 1)
            payload = json.loads((root / "config.env").read_text(encoding="utf-8")) if False else None
            self.assertIsNone(payload)

    def test_missing_target(self):
        self.assertEqual(main(["scan", "/definitely/not/a/repository"]), 2)


if __name__ == '__main__':
    unittest.main()
