import unittest

from check_data import get_checks


class GetChecksTests(unittest.TestCase):
    def test_returns_three_named_status_items(self) -> None:
        self.assertEqual(
            get_checks(),
            [
                {"name": "API応答", "status": "ok"},
                {"name": "エラーログ", "status": "needs_review"},
                {"name": "再試行回数", "status": "ok"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
