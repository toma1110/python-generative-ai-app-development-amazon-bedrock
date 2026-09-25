import unittest
import io
from contextlib import redirect_stderr
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError

import s05_l02
import s05_l03
import s05_l04
from bedrock_call import response_text, user_message


def response(text="確認項目を一つ挙げます。"):
    return {
        "output": {"message": {"content": [{"text": text}]}},
        "stopReason": "end_turn",
        "usage": {"inputTokens": 12, "outputTokens": 8, "totalTokens": 20},
        "metrics": {"latencyMs": 450},
    }


class SharedHelperTests(unittest.TestCase):
    def test_user_message_has_user_role_and_text_block(self):
        self.assertEqual(user_message("hello"), [{"role": "user", "content": [{"text": "hello"}]}])

    def test_response_text_reads_text_block(self):
        self.assertEqual(response_text(response("ok")), "ok")


class Lecture02Tests(unittest.TestCase):
    def test_calls_converse_once_with_one_user_message(self):
        client = Mock()
        client.converse.return_value = response()

        result = s05_l02.call_once(client)

        client.converse.assert_called_once()
        request = client.converse.call_args.kwargs
        self.assertEqual(request["messages"][0]["role"], "user")
        self.assertEqual(request["inferenceConfig"]["maxTokens"], 96)
        self.assertEqual(s05_l02.response_text(result), "確認項目を一つ挙げます。")


class Lecture03Tests(unittest.TestCase):
    def test_compares_baseline_system_only_and_parameter_only(self):
        client = Mock()
        client.converse.side_effect = [response("基準"), response("system"), response("parameter")]

        results = s05_l03.compare(client)

        self.assertEqual(len(results), 3)
        self.assertEqual(client.converse.call_count, 3)
        baseline, system_changed, parameter_changed = [call.kwargs for call in client.converse.call_args_list]
        self.assertNotIn("system", baseline)
        self.assertIn("system", system_changed)
        self.assertEqual(baseline["inferenceConfig"], system_changed["inferenceConfig"])
        self.assertNotIn("system", parameter_changed)
        self.assertNotEqual(baseline["inferenceConfig"], parameter_changed["inferenceConfig"])


class Lecture04Tests(unittest.TestCase):
    def test_reads_text_usage_stop_reason_and_latency(self):
        result = s05_l04.inspect_response(response("応答"))

        self.assertEqual(result, {
            "text": "応答",
            "stop_reason": "end_turn",
            "input_tokens": 12,
            "output_tokens": 8,
            "total_tokens": 20,
            "latency_ms": 450,
        })

    @patch("s05_l04.create_client")
    def test_api_client_error_returns_failure_without_echoing_error_message(self, create_client):
        client = Mock()
        client.converse.side_effect = ClientError(
            {"Error": {"Code": "AccessDeniedException", "Message": "do not print this detail"},
             "ResponseMetadata": {"RequestId": "example-request-id"}},
            "Converse",
        )
        create_client.return_value = client
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            result = s05_l04.main()

        self.assertEqual(result, 1)
        self.assertIn("AccessDeniedException", stderr.getvalue())
        self.assertIn("example-request-id", stderr.getvalue())
        self.assertNotIn("do not print this detail", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
