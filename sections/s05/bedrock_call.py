"""Shared helpers for the Section 05 one-turn Converse exercises."""

import os
import sys

import boto3

DEFAULT_MODEL_ID = "amazon.nova-lite-v1:0"
MAX_OUTPUT_TOKENS = 96


def create_client():
    """Create a Bedrock Runtime client from the active boto3 configuration."""
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
    return [{"role": "user", "content": [{"text": text}]}]


def response_text(response):
    """Read the first text block from a Converse response."""
    content = response["output"]["message"]["content"]
    for block in content:
        if "text" in block:
            return block["text"]
    raise ValueError("応答にtext content blockがありません。")
