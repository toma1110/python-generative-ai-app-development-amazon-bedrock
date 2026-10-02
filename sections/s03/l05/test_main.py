"""L05のファイル入力とJSON値検査を確認する。"""

import json
import tempfile
import unittest
from pathlib import Path

from main import load_checks, validate_checks


class ValidateChecksTests(unittest.TestCase):
    def test_accepts_expected_data(self) -> None:
        result = validate_checks([{"name": "API", "status": "ok"}])
        self.assertEqual(result[0]["name"], "API")

    def test_rejects_non_list(self) -> None:
        with self.assertRaisesRegex(ValueError, "最上位は配列"):
            validate_checks({"name": "API", "status": "ok"})

    def test_rejects_non_object_item(self) -> None:
        with self.assertRaisesRegex(ValueError, "オブジェクト"):
            validate_checks(["API"])

    def test_rejects_unknown_status(self) -> None:
        with self.assertRaisesRegex(ValueError, "status"):
            validate_checks([{"name": "API", "status": "unknown"}])


class LoadChecksTests(unittest.TestCase):
    def test_reads_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps([{"name": "API", "status": "ok"}]), encoding="utf-8")
            checks, error = load_checks(path)
        self.assertIsNone(error)
        self.assertEqual(checks, [{"name": "API", "status": "ok"}])

    def test_reports_missing_file(self) -> None:
        checks, error = load_checks(Path("no-such-cases.json"))
        self.assertIsNone(checks)
        self.assertIn("ファイルが見つかりません", error or "")

    def test_reports_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.json"
            path.write_text("{", encoding="utf-8")
            checks, error = load_checks(path)
        self.assertIsNone(checks)
        self.assertIn("JSONの形式", error or "")


if __name__ == "__main__":
    unittest.main()
