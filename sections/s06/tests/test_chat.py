import unittest

from bedrock_chat import converse_turn
from s06_l03 import chat as chat_l03
from s06_l04 import chat as chat_l04


class FakeClient:
    def __init__(self, answers=None, error=None):
        self.calls = []
        self.answers = iter(answers or ["回答です。"])
        self.error = error

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            error, self.error = self.error, None
            raise error
        return {"output": {"message": {"role": "assistant", "content": [{"text": next(self.answers)}]}}}


class ChatTests(unittest.TestCase):
    def test_turn_sends_user_message_and_retains_assistant_response(self):
        client = FakeClient(["こんにちは。"])
        history = []

        answer = converse_turn(client, history, "こんにちは")

        self.assertEqual(answer, "こんにちは。")
        self.assertEqual(client.calls[0]["messages"], [{"role": "user", "content": [{"text": "こんにちは"}]}])
        self.assertEqual([item["role"] for item in history], ["user", "assistant"])

    def test_history_mode_sends_prior_user_and_assistant_messages(self):
        client = FakeClient(["東京です。", "日本です。"])
        history = []
        converse_turn(client, history, "私は東京に住んでいます。")
        converse_turn(client, history, "私はどこに住んでいますか？")

        self.assertEqual(len(client.calls[1]["messages"]), 3)
        self.assertEqual(client.calls[1]["messages"][-1]["content"][0]["text"], "私はどこに住んでいますか？")

    def test_no_history_mode_sends_only_current_question(self):
        client = FakeClient(["回答1", "回答2"])
        history = []
        converse_turn(client, history, "前の質問", include_history=False)
        converse_turn(client, history, "続きの質問", include_history=False)

        self.assertEqual(len(client.calls[1]["messages"]), 1)
        self.assertEqual(client.calls[1]["messages"][0]["content"][0]["text"], "続きの質問")
        self.assertEqual(history, [])

    def test_cli_exits_on_command(self):
        client = FakeClient()
        prompts = iter(["/exit"])
        output = []

        result = chat_l03(client, input_fn=lambda _: next(prompts), output_fn=output.append)

        self.assertEqual(result, 0)
        self.assertEqual(client.calls, [])
        self.assertTrue(any("終了" in line for line in output))

    def test_cli_exits_cleanly_when_interrupted_during_request(self):
        client = FakeClient(error=KeyboardInterrupt())
        prompts = iter(["質問です"])
        output = []

        result = chat_l04(client, input_fn=lambda _: next(prompts), output_fn=output.append)

        self.assertEqual(result, 0)
        self.assertTrue(any("入力を終了" in line for line in output))

    def test_cli_continues_after_sanitized_client_error(self):
        from botocore.exceptions import ClientError

        error = ClientError(
            {"Error": {"Code": "AccessDeniedException", "Message": "sensitive payload"}, "ResponseMetadata": {"RequestId": "req-example"}},
            "Converse",
        )
        client = FakeClient(["復帰しました。"], error=error)
        prompts = iter(["最初の質問", "次の質問", "/exit"])
        output = []

        result = chat_l04(client, input_fn=lambda _: next(prompts), output_fn=output.append)

        self.assertEqual(result, 0)
        self.assertEqual(len(client.calls), 2)
        self.assertTrue(any("AccessDeniedException" in line for line in output))
        self.assertTrue(any("req-example" in line for line in output))
        self.assertFalse(any("sensitive payload" in line for line in output))
        self.assertTrue(any("復帰しました。" in line for line in output))


if __name__ == "__main__":
    unittest.main()
