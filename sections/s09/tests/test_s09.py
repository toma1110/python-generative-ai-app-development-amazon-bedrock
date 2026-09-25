import unittest
from io import BytesIO
from unittest.mock import Mock
from botocore.exceptions import ClientError

from s09_app import load_note
from s09_common import ask_model, response_metrics
from s09_l02 import OBJECT_KEY, prepare_bucket
from s09_l03 import read_s3_text
from s09_l06 import BASELINE_PROMPT, REVISED_PROMPT, compare


def response(text="応答"):
    return {
        "output": {"message": {"content": [{"text": text}]}},
        "usage": {"inputTokens": 11, "outputTokens": 7},
        "metrics": {"latencyMs": 100},
    }


class Section09Tests(unittest.TestCase):
    def test_setup_creates_only_requested_bucket_and_fixed_object(self):
        s3 = Mock()
        s3.head_bucket.side_effect = ClientError(
            {"Error": {"Code": "404"}, "ResponseMetadata": {"HTTPStatusCode": 404}}, "HeadBucket"
        )
        self.assertEqual(prepare_bucket(s3, "example-unique-bucket", "us-west-2", b"memo"), OBJECT_KEY)
        s3.create_bucket.assert_called_once_with(
            Bucket="example-unique-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        s3.put_object.assert_called_once_with(
            Bucket="example-unique-bucket", Key=OBJECT_KEY, Body=b"memo", ContentType="text/plain; charset=utf-8"
        )

    def test_setup_refuses_existing_bucket_without_writing(self):
        s3 = Mock()
        s3.head_bucket.return_value = {}
        with self.assertRaisesRegex(ValueError, "既に存在"):
            prepare_bucket(s3, "existing", "us-east-1", b"memo")
        s3.create_bucket.assert_not_called()
        s3.put_object.assert_not_called()

    def test_s3_read_uses_exact_bucket_and_key_and_closes_body(self):
        body = BytesIO("架空メモ".encode())
        s3 = Mock()
        s3.get_object.return_value = {"Body": body}
        self.assertEqual(read_s3_text(s3, "demo-bucket", OBJECT_KEY), "架空メモ")
        s3.get_object.assert_called_once_with(Bucket="demo-bucket", Key=OBJECT_KEY)
        self.assertTrue(body.closed)

    def test_local_and_s3_are_loaded_through_one_app_entry_point(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            path = Path(directory) / "memo.txt"
            path.write_text("local memo", encoding="utf-8")
            self.assertEqual(load_note("local", path, None, OBJECT_KEY), "local memo")

    def test_model_request_reports_text_usage_and_safe_system_instruction(self):
        client = Mock()
        client.converse.return_value = response("要約")
        result = ask_model(client, "架空メモ", "summary")
        request = client.converse.call_args.kwargs
        self.assertEqual(result, {"text": "要約", "input_tokens": 11, "output_tokens": 7, "latency_ms": 100})
        self.assertIn("断定しません", request["system"][0]["text"])
        self.assertIn("架空メモ", request["messages"][0]["content"][0]["text"])

    def test_comparison_uses_identical_note_with_two_different_prompts(self):
        client = Mock()
        client.converse.side_effect = [response("前"), response("後")]
        results = compare(client, "same note")
        self.assertNotEqual(BASELINE_PROMPT, REVISED_PROMPT)
        self.assertEqual(client.converse.call_count, 2)
        self.assertEqual(
            [call.kwargs["messages"][0]["content"][0]["text"].split("--- 調査メモ ---\n", 1)[1]
             for call in client.converse.call_args_list],
            ["same note", "same note"],
        )
        self.assertEqual(
            [label for label, _ in results],
            ["BASELINE（既存の短い要約指示）", "REVISED（編集対象の指示）"],
        )

    def test_missing_metrics_are_reported_as_unknown(self):
        self.assertEqual(response_metrics({}), {"input_tokens": "不明", "output_tokens": "不明", "latency_ms": "不明"})


if __name__ == "__main__":
    unittest.main()
