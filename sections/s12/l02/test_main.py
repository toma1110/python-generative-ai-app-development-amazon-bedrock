import unittest

from main import classify_check


class ClassifyCheckTests(unittest.TestCase):
    def test_needs_review_returns_guidance(self) -> None:
        self.assertEqual(
            classify_check({"name": "エラーログ", "status": "needs_review"}),
            "追加確認が必要",
        )

    def test_other_status_returns_confirmed(self) -> None:
        self.assertEqual(
            classify_check({"name": "API応答", "status": "ok"}), "確認済み"
        )


if __name__ == "__main__":
    unittest.main()
