import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import Mock, patch

from botocore.exceptions import NoCredentialsError

import main


class ReadTargetTests(unittest.TestCase):
    def test_returns_account_and_configured_region(self):
        sts = Mock()
        sts.get_caller_identity.return_value = {
            "Account": "example-account-id",
        }
        session = Mock(region_name="ap-northeast-1")
        session.client.return_value = sts

        self.assertEqual(
            main.read_target(session), ("example-account-id", "ap-northeast-1")
        )
        session.client.assert_called_once_with("sts", region_name="ap-northeast-1")
        sts.get_caller_identity.assert_called_once_with()

    def test_requires_a_region_before_calling_sts(self):
        session = Mock(region_name=None)

        with self.assertRaises(main.RegionNotConfiguredError):
            main.read_target(session)

        session.client.assert_not_called()


class MainTests(unittest.TestCase):
    @patch("main.read_target", return_value=("example-account-id", "ap-northeast-1"))
    def test_prints_only_account_and_region(self, _read_target):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            result = main.main()

        self.assertEqual(result, 0)
        self.assertEqual(
            stdout.getvalue(),
            "接続先アカウント: example-account-id\n接続先リージョン: ap-northeast-1\n",
        )

    @patch("main.read_target", side_effect=NoCredentialsError())
    def test_does_not_print_credential_details_on_failure(self, _read_target):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = main.main()

        self.assertEqual(result, 1)
        self.assertIn("プロファイル、ログイン状態", stderr.getvalue())
        self.assertNotIn("AKIA", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
