"""Shared helpers for the Section 06 CLI chat exercises."""

import os
import sys

import boto3

DEFAULT_MODEL_ID = "amazon.nova-lite-v1:0"
MAX_OUTPUT_TOKENS = 128


def configure_console():
    """Use UTF-8 for Japanese output when the terminal supports reconfiguration."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def create_client():
    """Create a Bedrock Runtime client using boto3's normal credential chain."""
    return boto3.Session().client("bedrock-runtime")


def model_id():
    """Return the configured model ID, defaulting to Nova Lite."""
    return os.environ.get("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID)


def message(role, text):
    return {"role": role, "content": [{"text": text}]}


def response_text(response):
    """Read the first text content block from a Converse response."""
    for block in response["output"]["message"]["content"]:
        if "text" in block:
            return block["text"]
    raise ValueError("応答にtext content blockがありません。")


def converse_turn(client, history, user_text, include_history=True):
    """Send one turn and retain the exchange only when history is enabled."""
    user_message = message("user", user_text)
    messages = [*history, user_message] if include_history else [user_message]
    response = client.converse(
        modelId=model_id(),
        messages=messages,
        inferenceConfig={"maxTokens": MAX_OUTPUT_TOKENS},
    )
    answer = response_text(response)
    if include_history:
        history.extend((user_message, response["output"]["message"]))
    return answer
