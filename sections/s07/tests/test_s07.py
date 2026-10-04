import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from s07_app import EmptyInputError, IncompleteResponseError, InputTooLongError, read_text_file, summarize_text, validate_input
from s07_l02 import main as l02_main
from s07_l04 import main as l04_main


class FakeClient:
    def __init__(self, response=None):
        self.calls = []
        self.response = response or {
            "stopReason": "end_turn",
            "output": {"message": {"content": [{"text": "確認できた事実の要約です。"}]}}
        }

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


class FileInputTests(unittest.TestCase):
    def test_reads_utf8_text_and_trims_outer_whitespace(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memo.txt"
            path.write_text("\n調査メモです。\n", encoding="utf-8")

            self.assertEqual(read_text_file(path), "調査メモです。")

    def test_rejects_blank_input(self):
        with self.assertRaises(EmptyInputError):
            validate_input(" \n\t ")

    def test_rejects_input_above_the_exercise_limit(self):
        with self.assertRaises(InputTooLongError):
            validate_input("x" * 12001)

    def test_l04_reports_oversized_file_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "long.txt"
            path.write_text("x" * 12001, encoding="utf-8")
            error_output = StringIO()

            with redirect_stderr(error_output):
                result = l04_main(["--file", str(path)])

        self.assertEqual(result, 2)
        self.assertIn("12000文字", error_output.getvalue())
        self.assertNotIn("Traceback", error_output.getvalue())

    def test_missing_file_is_distinct_from_blank_file(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.txt"
            blank = Path(directory) / "blank.txt"
            blank.write_text(" \n", encoding="utf-8")

            with self.assertRaises(FileNotFoundError):
                read_text_file(missing)
            with self.assertRaises(EmptyInputError):
                read_text_file(blank)

    def test_rejects_non_utf8_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.txt"
            path.write_bytes(b"\xff\xfe")

            with self.assertRaises(UnicodeDecodeError):
                read_text_file(path)

    def test_summary_uses_file_text_and_a_bounded_converse_request(self):
        client = FakeClient()

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memo.txt"
            path.write_text("  原文の内容  ", encoding="utf-8")
            source = read_text_file(path)
        result = summarize_text(client, source)

        self.assertEqual(result, "確認できた事実の要約です。")
        self.assertEqual(len(client.calls), 1)
        request = client.calls[0]
        self.assertEqual(request["modelId"], "amazon.nova-lite-v1:0")
        self.assertEqual(request["inferenceConfig"]["maxTokens"], 256)
        self.assertEqual(request["messages"][0]["content"][0]["text"], "次の調査メモを要約してください。\n\n原文の内容")

    def test_max_tokens_response_is_not_returned_as_a_complete_summary(self):
        client = FakeClient({
            "stopReason": "max_tokens",
            "output": {"message": {"content": [{"text": "途中までの出力"}]}},
        })

        with self.assertRaisesRegex(IncompleteResponseError, "出力上限で途中終了"):
            summarize_text(client, "原文の内容")

        self.assertEqual(len(client.calls), 1)

    def test_response_without_text_is_distinguished_from_completed_summary(self):
        client = FakeClient({
            "stopReason": "end_turn",
            "output": {"message": {"content": [{"image": {"format": "png", "source": {}}}]}},
        })

        with self.assertRaisesRegex(ValueError, "応答に要約テキストがありません"):
            summarize_text(client, "原文の内容")

    def test_empty_input_does_not_call_the_model(self):
        client = FakeClient()

        with self.assertRaises(EmptyInputError):
            summarize_text(client, "")

        self.assertEqual(client.calls, [])

    def test_api_free_file_tests_do_not_create_a_bedrock_client(self):
        # File validation operates on local text and has no client parameter.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memo.txt"
            path.write_text("ローカルだけで確認", encoding="utf-8")
            self.assertIn("ローカル", read_text_file(path))

    def test_missing_file_stops_before_bedrock_client_is_created(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.txt"
            error_output = StringIO()
            from unittest.mock import patch

            with patch("s07_l02.create_client") as create_client, redirect_stderr(error_output):
                result = l02_main(["--file", str(missing)])

        self.assertEqual(result, 2)
        self.assertIn("ファイルが見つかりません", error_output.getvalue())
        create_client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
