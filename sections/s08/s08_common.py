"""Shared helpers for the Section 08 evaluation exercises."""

import os
import sys

import boto3

DEFAULT_MODEL_ID = "amazon.nova-lite-v1:0"
MAX_OUTPUT_TOKENS = 160


def create_client():
    return boto3.Session().client("bedrock-runtime")


def configure_console():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def model_id():
    return os.environ.get("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID)


def message(role, text):
    return {"role": role, "content": [{"text": text}]}


def response_text(response):
    for block in response["output"]["message"]["content"]:
        if "text" in block:
            return block["text"]
    raise ValueError("応答にtext content blockがありません。")


def response_metrics(response):
    usage = response.get("usage", {})
    metrics = response.get("metrics", {})
    return {
        "input_tokens": usage.get("inputTokens", "不明"),
        "output_tokens": usage.get("outputTokens", "不明"),
        "total_tokens": usage.get("totalTokens", "不明"),
        "latency_ms": metrics.get("latencyMs", "不明"),
    }


def converse(client, messages, system_text, max_tokens=MAX_OUTPUT_TOKENS):
    request = {
        "modelId": model_id(),
        "messages": messages,
        "inferenceConfig": {"maxTokens": max_tokens},
    }
    if system_text:
        request["system"] = [{"text": system_text}]
    return client.converse(**request)


def keep_recent_turns(history, turn_count):
    """Return complete user/assistant turn pairs, or no history for zero."""
    if turn_count < 0:
        raise ValueError("履歴ターン数は0以上にしてください。")
    complete_turns = len(history) // 2
    if turn_count == 0:
        return []
    return history[-min(turn_count, complete_turns) * 2 :]
