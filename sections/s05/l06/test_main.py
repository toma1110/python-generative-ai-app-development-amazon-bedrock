import json
import tempfile
import unittest
from pathlib import Path
from main import load_checks


class LoadChecksTests(unittest.TestCase):
    def test_returns_checks_and_no_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps([{"name": "API", "status": "ok"}]), encoding="utf-8")
            checks, error = load_checks(path)
        self.assertEqual(checks, [{"name": "API", "status": "ok"}])
        self.assertIsNone(error)

    def test_returns_no_checks_and_validation_message(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps([{"name": "API", "status": "unknown"}]), encoding="utf-8")
            checks, error = load_checks(path)
        self.assertIsNone(checks)
        self.assertRegex(error or "", "status")


if __name__ == "__main__":
    unittest.main()
