import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError, NoCredentialsError

import main


class ReadTargetTests(unittest.TestCase):
    def test_returns_account_and_configured_region(self):
        sts = Mock()
        sts.get_caller_identity.return_value = {
            "Account": "example-account-id",
        }
        session = Mock()
        session.client.return_value = sts

        self.assertEqual(
            main.read_target(session, "ap-northeast-1"), "example-account-id"
        )
        session.client.assert_called_once_with("sts", region_name="ap-northeast-1")
        sts.get_caller_identity.assert_called_once_with()


class MainTests(unittest.TestCase):
    @patch("main.read_target", return_value="example-account-id")
    @patch("main.boto3.Session")
    def test_prints_only_account_and_region(self, session_factory, _read_target):
        session_factory.return_value.region_name = "ap-northeast-1"
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            result = main.main()

        self.assertEqual(result, 0)
        self.assertEqual(
            stdout.getvalue(),
            "接続先アカウント: example-account-id\n接続先リージョン: ap-northeast-1\n",
        )

    @patch("main.read_target", side_effect=NoCredentialsError())
    @patch("main.boto3.Session")
    def test_does_not_print_credential_details_on_failure(
        self, session_factory, _read_target
    ):
        session_factory.return_value.region_name = "ap-northeast-1"
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = main.main()

        self.assertEqual(result, 1)
        self.assertIn("プロファイル、ログイン状態", stderr.getvalue())
        self.assertNotIn("AKIA", stderr.getvalue())

    @patch(
        "main.read_target",
        side_effect=ClientError(
            {
                "Error": {
                    "Code": "InvalidClientTokenId",
                    "Message": "sensitive response detail AKIAEXAMPLE",
                }
            },
            "GetCallerIdentity",
        ),
    )
    @patch("main.boto3.Session")
    def test_client_error_does_not_leak_response_or_traceback(
        self, session_factory, _read_target
    ):
        session_factory.return_value.region_name = "ap-northeast-1"
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = main.main()

        self.assertEqual(result, 1)
        self.assertIn("AWS接続を確認できませんでした", stderr.getvalue())
        self.assertNotIn("InvalidClientTokenId", stderr.getvalue())
        self.assertNotIn("sensitive response detail", stderr.getvalue())
        self.assertNotIn("AKIAEXAMPLE", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    @patch("main.boto3.Session")
    def test_region_must_be_configured_before_an_sts_request(self, session_factory):
        session = session_factory.return_value
        session.region_name = None
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = main.main()

        self.assertEqual(result, 1)
        session.client.assert_not_called()
        self.assertIn("リージョンが設定されていません", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
