import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from s07_app import EmptyInputError, IncompleteResponseError, InputTooLongError, read_text_file, save_summary, summarize_text, validate_input
from s07_l02 import main as l02_main
from s07_l04 import main as l04_main

TEST_INPUT = "この文章はテスト用に用意した架空の調査メモ本文です。入力境界も併せて確認します。"
MAX_INPUT_CHARACTERS = 12000


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
    def test_save_summary_writes_utf8_markdown_with_input_basename(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "調査メモ.txt"
            source.write_text(TEST_INPUT, encoding="utf-8")
            output = Path(directory) / "report.md"

            saved = save_summary(source, output, "確認できた事実の要約です。")

            self.assertEqual(saved, output)
            self.assertEqual(
                output.read_bytes().decode("utf-8"),
                "# 要約: 調査メモ.txt\n\n確認できた事実の要約です。\n\n> 要約は原文と照合して利用してください。\n",
            )

    def test_save_summary_does_not_replace_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "memo.txt"
            output = Path(directory) / "report.md"
            source.write_text(TEST_INPUT, encoding="utf-8")
            output.write_text("keep", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "既にあります"):
                save_summary(source, output, "new")

            self.assertEqual(output.read_text(encoding="utf-8"), "keep")

    def test_l02_saves_fake_summary_and_default_mode_keeps_stdout(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "memo.txt"
            output = Path(directory) / "report.md"
            source.write_text(TEST_INPUT, encoding="utf-8")
            fake = FakeClient()
            stdout = StringIO()
            from unittest.mock import patch

            with patch("s07_l02.create_client", return_value=fake), redirect_stdout(stdout):
                result = l02_main(["--file", str(source), "--output", str(output)])

            self.assertEqual(result, 0)
            self.assertEqual(len(fake.calls), 1)
            self.assertIn("# 要約: memo.txt", output.read_text(encoding="utf-8"))
            self.assertIn("要約を保存しました", stdout.getvalue())

            stdout = StringIO()
            with patch("s07_l02.create_client", return_value=FakeClient()), redirect_stdout(stdout):
                result = l02_main(["--file", str(source)])

            self.assertEqual(result, 0)
            self.assertIn("要約（原文と照合して利用してください）:", stdout.getvalue())
            self.assertIn("確認できた事実の要約です。", stdout.getvalue())

    def test_known_invalid_output_stops_before_client_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "memo.txt"
            output = Path(directory) / "existing.md"
            source.write_text(TEST_INPUT, encoding="utf-8")
            output.write_text("keep", encoding="utf-8")
            error_output = StringIO()
            from unittest.mock import patch

            with patch("s07_l02.create_client") as create_client, redirect_stderr(error_output):
                result = l02_main(["--file", str(source), "--output", str(output)])

            self.assertEqual(result, 2)
            self.assertIn("既にあります", error_output.getvalue())
            create_client.assert_not_called()
            self.assertEqual(output.read_text(encoding="utf-8"), "keep")

    def test_input_file_cannot_be_used_as_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "memo.txt"
            source.write_text(TEST_INPUT, encoding="utf-8")
            error_output = StringIO()
            from unittest.mock import patch

            with patch("s07_l02.create_client") as create_client, redirect_stderr(error_output):
                result = l02_main(["--file", str(source), "--output", str(source)])

            self.assertEqual(result, 2)
            self.assertIn("既にあります", error_output.getvalue())
            create_client.assert_not_called()
            self.assertEqual(source.read_text(encoding="utf-8"), TEST_INPUT)

    def test_missing_output_parent_stops_before_client_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "memo.txt"
            source.write_text(TEST_INPUT, encoding="utf-8")
            output = Path(directory) / "missing" / "report.md"
            error_output = StringIO()
            from unittest.mock import patch

            with patch("s07_l02.create_client") as create_client, redirect_stderr(error_output):
                result = l02_main(["--file", str(source), "--output", str(output)])

            self.assertEqual(result, 2)
            self.assertIn("フォルダーがありません", error_output.getvalue())
            create_client.assert_not_called()
            self.assertFalse(output.parent.exists())

    def test_api_failure_does_not_create_report(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "memo.txt"
            output = Path(directory) / "report.md"
            source.write_text(TEST_INPUT, encoding="utf-8")
            fake = FakeClient({"stopReason": "max_tokens", "output": {"message": {"content": [{"text": "途中"}]}}})
            error_output = StringIO()
            from unittest.mock import patch

            with patch("s07_l02.create_client", return_value=fake), redirect_stderr(error_output):
                result = l02_main(["--file", str(source), "--output", str(output)])

            self.assertEqual(result, 1)
            self.assertIn("途中終了", error_output.getvalue())
            self.assertFalse(output.exists())

    def test_write_failure_is_reported_without_success_message(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "memo.txt"
            output = Path(directory) / "report.md"
            source.write_text(TEST_INPUT, encoding="utf-8")
            fake = FakeClient()
            error_output = StringIO()
            stdout = StringIO()
            from unittest.mock import patch

            with patch("s07_l02.create_client", return_value=fake), patch("s07_l02.save_summary", side_effect=OSError("disk full")), redirect_stderr(error_output), redirect_stdout(stdout):
                result = l02_main(["--file", str(source), "--output", str(output)])

            self.assertEqual(result, 1)
            self.assertIn("disk full", error_output.getvalue())
            self.assertNotIn("保存しました", stdout.getvalue())
            self.assertFalse(output.exists())

    def test_partial_write_failure_is_reported_and_partial_file_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "memo.txt"
            output = Path(directory) / "report.md"
            source.write_text(TEST_INPUT, encoding="utf-8")
            fake = FakeClient()
            error_output = StringIO()
            stdout = StringIO()
            from unittest.mock import patch

            original_open = Path.open

            class PartialWriter:
                def __init__(self, stream):
                    self.stream = stream

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc_value, traceback):
                    self.stream.close()
                    return False

                def write(self, content):
                    self.stream.write(content[:12])
                    self.stream.flush()
                    raise OSError("disk full")

            def open_with_partial_failure(path, *args, **kwargs):
                if path == output:
                    return PartialWriter(original_open(path, *args, **kwargs))
                return original_open(path, *args, **kwargs)

            with patch("s07_l02.create_client", return_value=fake), patch.object(Path, "open", open_with_partial_failure), redirect_stderr(error_output), redirect_stdout(stdout):
                result = l02_main(["--file", str(source), "--output", str(output)])

            self.assertEqual(result, 1)
            self.assertIn("disk full", error_output.getvalue())
            self.assertIn("空き容量", error_output.getvalue())
            self.assertIn("不完全なファイルが残っている場合", error_output.getvalue())
            self.assertIn("別のファイル名", error_output.getvalue())
            self.assertNotIn("保存しました", stdout.getvalue())
            self.assertTrue(output.exists())
            self.assertEqual(output.read_text(encoding="utf-8"), "# 要約: memo.t")

    def test_reads_utf8_text_and_trims_outer_whitespace(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memo.txt"
            path.write_text(f"\n{TEST_INPUT}\n", encoding="utf-8")

            self.assertEqual(read_text_file(path), TEST_INPUT)

    def test_rejects_blank_input(self):
        with self.assertRaises(EmptyInputError):
            validate_input(" \n\t ")

    def test_accepts_one_character_after_trimming(self):
        self.assertEqual(validate_input("  x  "), "x")

    def test_accepts_input_at_the_maximum_length(self):
        text = "x" * MAX_INPUT_CHARACTERS
        self.assertEqual(validate_input(text), text)

    def test_accepts_input_below_the_maximum_length(self):
        text = "x" * (MAX_INPUT_CHARACTERS - 1)
        self.assertEqual(validate_input(text), text)

    def test_rejects_input_above_the_exercise_limit(self):
        with self.assertRaises(InputTooLongError):
            validate_input("x" * (MAX_INPUT_CHARACTERS + 1))

    def test_l04_accepts_short_meaningful_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "short.txt"
            path.write_text("x", encoding="utf-8")
            output = StringIO()

            with redirect_stdout(output):
                result = l04_main(["--file", str(path)])

        self.assertEqual(result, 0)
        self.assertIn("1文字の入力を読み込みました", output.getvalue())

    def test_l04_reports_blank_file_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "blank.txt"
            path.write_text(" \n", encoding="utf-8")
            error_output = StringIO()

            with redirect_stderr(error_output):
                result = l04_main(["--file", str(path)])

        self.assertEqual(result, 2)
        self.assertIn("内容が空", error_output.getvalue())
        self.assertNotIn("Traceback", error_output.getvalue())

    def test_l04_reports_oversized_file_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "long.txt"
            path.write_text("x" * (MAX_INPUT_CHARACTERS + 1), encoding="utf-8")
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
            path.write_text(f"  {TEST_INPUT}  ", encoding="utf-8")
            source = read_text_file(path)
        result = summarize_text(client, source)

        self.assertEqual(result, "確認できた事実の要約です。")
        self.assertEqual(len(client.calls), 1)
        request = client.calls[0]
        self.assertEqual(request["modelId"], "amazon.nova-lite-v1:0")
        self.assertEqual(request["inferenceConfig"]["maxTokens"], 512)
        self.assertIn("日本語で100字程度", request["system"][0]["text"])
        self.assertEqual(request["messages"][0]["content"][0]["text"], f"次の調査メモを要約してください。\n\n{TEST_INPUT}")

    def test_max_tokens_response_is_not_returned_as_a_complete_summary(self):
        client = FakeClient({
            "stopReason": "max_tokens",
            "output": {"message": {"content": [{"text": "途中までの出力"}]}},
        })

        with self.assertRaisesRegex(IncompleteResponseError, "出力上限で途中終了"):
            summarize_text(client, TEST_INPUT)

        self.assertEqual(len(client.calls), 1)

    def test_response_without_text_is_distinguished_from_completed_summary(self):
        client = FakeClient({
            "stopReason": "end_turn",
            "output": {"message": {"content": [{"image": {"format": "png", "source": {}}}]}},
        })

        with self.assertRaisesRegex(ValueError, "応答に要約テキストがありません"):
            summarize_text(client, TEST_INPUT)

    def test_empty_input_does_not_call_the_model(self):
        client = FakeClient()

        with self.assertRaises(EmptyInputError):
            summarize_text(client, "")

        self.assertEqual(client.calls, [])

    def test_short_meaningful_input_is_sent_to_the_stub(self):
        client = FakeClient()

        result = summarize_text(client, "x")

        self.assertEqual(result, "確認できた事実の要約です。")
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(client.calls[0]["messages"][0]["content"][0]["text"], "次の調査メモを要約してください。\n\nx")

    def test_api_free_file_tests_do_not_create_a_bedrock_client(self):
        # File validation operates on local text and has no client parameter.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memo.txt"
            path.write_text(TEST_INPUT, encoding="utf-8")
            self.assertIn("調査メモ", read_text_file(path))

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
