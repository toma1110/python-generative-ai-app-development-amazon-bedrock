"""Shared helpers for the Section 05 one-turn Converse exercises."""

import os
import sys

import boto3

DEFAULT_MODEL_ID = "amazon.nova-lite-v1:0"
MAX_OUTPUT_TOKENS = 96


def create_client():
    """Create an SDK object configured for Bedrock Runtime.

    boto3 resolves the active profile's credentials and Region from the normal
    AWS configuration chain; the program does not read or print credentials.
    """
    return boto3.Session().client("bedrock-runtime")


def configure_console():
    """Use UTF-8 for Japanese output when the terminal supports reconfiguration."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def model_id():
    """Return the configured model ID, defaulting to Nova Lite."""
    return os.environ.get("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID)


def user_message(text):
    """Place text in the nested message shape expected by Converse."""
    return [{"role": "user", "content": [{"text": text}]}]


def response_text(response):
    """Follow output → message → content and return its first text block.

    Converse returns dictionaries and lists. `output` contains a `message`,
    whose `content` list contains one or more blocks such as `{"text": ...}`.
    """
    content = response["output"]["message"]["content"]
    for block in content:
        if "text" in block:
            return block["text"]
    raise ValueError("応答にtext content blockがありません。")
