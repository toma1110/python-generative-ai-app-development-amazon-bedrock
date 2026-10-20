import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
from unittest.mock import patch

from s08_common import (
    MAX_OUTPUT_TOKENS,
    IncompleteResponseError,
    create_client,
    keep_recent_turns,
    message,
    response_metrics,
    response_text,
)
from s08_l03 import BASELINE_PROMPT, REVISED_PROMPT, build_user_text, compare
from s08_l04 import QUESTIONS, parse_args, request_messages, run_turn


def fake_response(text, input_tokens=20):
    return {
        "output": {"message": {"content": [{"text": text}]}},
        "stopReason": "end_turn",
        "usage": {"inputTokens": input_tokens, "outputTokens": 5, "totalTokens": input_tokens + 5},
        "metrics": {"latencyMs": 321},
    }


class Section08Tests(unittest.TestCase):
    def test_configured_output_cap_is_512(self):
        self.assertEqual(MAX_OUTPUT_TOKENS, 512)

    def test_response_must_end_the_turn_before_text_is_used(self):
        self.assertEqual(response_text(fake_response("complete")), "complete")
        for reason in ("max_tokens", "content_filtered", None):
            with self.subTest(stop_reason=reason), self.assertRaises(IncompleteResponseError):
                response_text({**fake_response("partial"), "stopReason": reason})

    def test_client_disables_sdk_retries_for_billable_inference(self):
        with patch("s08_common.boto3.Session") as session_factory:
            create_client()
        config = session_factory.return_value.client.call_args.kwargs["config"]
        self.assertEqual(config.retries["total_max_attempts"], 1)

    def test_l03_uses_identical_case_with_distinct_prompts(self):
        note = "架空の障害メモ"
        self.assertNotEqual(BASELINE_PROMPT, REVISED_PROMPT)
        self.assertEqual(build_user_text(note, BASELINE_PROMPT).split("--- 調査メモ ---")[1],
                         build_user_text(note, REVISED_PROMPT).split("--- 調査メモ ---")[1])

    def test_l03_calls_once_per_prompt_and_reports_usage(self):
        client = Mock()
        client.converse.side_effect = [fake_response("before"), fake_response("after", 25)]
        results = list(compare(client, "同じケース"))
        self.assertEqual(client.converse.call_count, 2)
        self.assertEqual([item["text"] for item in results], ["before", "after"])
        self.assertEqual(results[1]["input_tokens"], 25)
        before, after = [call.kwargs for call in client.converse.call_args_list]
        self.assertEqual(before["system"], after["system"])
        self.assertEqual(before["modelId"], after["modelId"])
        self.assertEqual(before["inferenceConfig"], after["inferenceConfig"])
        self.assertNotEqual(before["messages"], after["messages"])
        for request in (before, after):
            self.assertIn("同じケース", request["messages"][0]["content"][0]["text"])
            self.assertEqual(request["inferenceConfig"]["maxTokens"], 512)

    def test_l03_yields_first_complete_result_before_second_call(self):
        client = Mock()
        client.converse.side_effect = [
            fake_response("before"),
            {**fake_response("partial"), "stopReason": "max_tokens"},
        ]
        results = compare(client, "同じケース")
        self.assertEqual(next(results)["text"], "before")
        with self.assertRaises(IncompleteResponseError):
            next(results)
        self.assertEqual(client.converse.call_count, 2)

    def test_history_keeps_complete_recent_pairs(self):
        history = [message("user", "a"), message("assistant", "A"),
                   message("user", "b"), message("assistant", "B")]
        self.assertEqual(keep_recent_turns(history, 1), history[-2:])
        self.assertEqual(keep_recent_turns(history, 0), [])
        self.assertEqual(keep_recent_turns(history, 5), history)
        with self.assertRaises(ValueError):
            keep_recent_turns(history, -1)

    def test_current_question_is_kept_when_history_is_disabled(self):
        history = [message("user", "old"), message("assistant", "old answer")]
        self.assertEqual(request_messages(history, "new", 0), [message("user", "new")])

    def test_l04_returns_metrics_and_appends_answer(self):
        client = Mock()
        client.converse.return_value = fake_response("answer")
        result = run_turn(client, [], "question", 2)
        self.assertEqual(result["text"], "answer")
        self.assertEqual(result["input_tokens"], 20)
        self.assertGreaterEqual(result["client_elapsed_ms"], 0)
        self.assertEqual(client.converse.call_args.kwargs["messages"], [message("user", "question")])

    def test_l04_main_is_bounded_to_two_fixed_sample_questions(self):
        client = Mock()
        client.converse.side_effect = [fake_response("answer one"), fake_response("answer two")]
        with TemporaryDirectory() as temp_dir:
            sample_path = Path(temp_dir) / "incident-note.txt"
            sample_path.write_text("架空の教材データ", encoding="utf-8")
            with patch("s08_l04.SAMPLE_PATH", sample_path), patch("s08_l04.create_client", return_value=client):
                with redirect_stdout(StringIO()):
                    from s08_l04 import main

                    self.assertEqual(main(["--history-turns", "2"]), 0)
        self.assertEqual(len(QUESTIONS), 2)
        self.assertEqual(client.converse.call_count, 2)
        second_request = client.converse.call_args_list[1].kwargs["messages"]
        self.assertEqual([item["role"] for item in second_request], ["user", "assistant", "user"])
        self.assertIn("架空の教材データ", second_request[-1]["content"][0]["text"])
        self.assertIn(QUESTIONS[1], second_request[-1]["content"][0]["text"])

    def test_l04_main_stops_without_retry_on_incomplete_response(self):
        client = Mock()
        client.converse.side_effect = [
            {**fake_response("partial"), "stopReason": "max_tokens"},
            fake_response("must not run"),
        ]
        with TemporaryDirectory() as temp_dir:
            sample_path = Path(temp_dir) / "incident-note.txt"
            sample_path.write_text("架空の教材データ", encoding="utf-8")
            with patch("s08_l04.SAMPLE_PATH", sample_path), patch("s08_l04.create_client", return_value=client):
                from s08_l04 import main
                with redirect_stdout(StringIO()), patch("s08_l04.sys.stderr", new_callable=StringIO) as stderr:
                    self.assertEqual(main(["--history-turns", "2"]), 1)
        self.assertEqual(client.converse.call_count, 1)
        self.assertIn("この応答を比較や会話履歴に使わず", stderr.getvalue())

    def test_args_reject_negative_history_count(self):
        with self.assertRaises(SystemExit):
            parse_args(["--history-turns", "-1"])

    def test_missing_metrics_are_shown_as_unknown(self):
        self.assertEqual(response_metrics({}), {
            "input_tokens": "不明", "output_tokens": "不明", "total_tokens": "不明", "latency_ms": "不明"
        })


if __name__ == "__main__":
    unittest.main()
