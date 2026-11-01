import json
import tempfile
import unittest
from pathlib import Path
from main import load_checks


class LoadChecksTests(unittest.TestCase):
    def test_reads_json_as_python_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps([{"name": "API", "status": "ok"}]), encoding="utf-8")
            checks = load_checks(path)
        self.assertEqual(checks, [{"name": "API", "status": "ok"}])

    def test_missing_path_is_a_file_not_found_error(self):
        with self.assertRaises(FileNotFoundError):
            load_checks(Path("no-such-cases.json"))

    def test_malformed_json_is_a_decode_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                load_checks(path)


if __name__ == "__main__":
    unittest.main()
