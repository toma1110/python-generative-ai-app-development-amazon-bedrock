"""Read and summarize a local UTF-8 text file with Amazon Bedrock."""

from pathlib import Path
import os

DEFAULT_MODEL_ID = "amazon.nova-lite-v1:0"
MAX_OUTPUT_TOKENS = 256
MAX_INPUT_CHARACTERS = 12000
SYSTEM_PROMPT = (
    "あなたは調査メモを短く要約するアシスタントです。"
    "メモに書かれた事実だけを使い、原因や復旧状況を推測で補わないでください。"
    "不明な項目は不明と明記し、対応を指示しないでください。"
)


class EmptyInputError(ValueError):
    """Raised when a text file contains no usable text."""


class InputTooLongError(ValueError):
    """Raised when a text file exceeds the exercise's input-size guard."""


def validate_input(text):
    """Return trimmed input text or raise a clear error for blank content."""
    if not isinstance(text, str) or not text.strip():
        raise EmptyInputError("ファイルの内容が空です。テキストを追加してください。")
    cleaned = text.strip()
    if len(cleaned) > MAX_INPUT_CHARACTERS:
        raise InputTooLongError(f"入力が{MAX_INPUT_CHARACTERS}文字を超えています。短いテキストファイルを指定してください。")
    return cleaned


def read_text_file(path):
    """Read a UTF-8 text file and reject files containing only whitespace."""
    text = Path(path).read_text(encoding="utf-8")
    return validate_input(text)


def summarize_text(client, text, model_id=DEFAULT_MODEL_ID):
    """Send one local text file to Converse and return its first text block."""
    source = validate_input(text)
    response = client.converse(
        modelId=model_id,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": f"次の調査メモを要約してください。\n\n{source}"}]}],
        inferenceConfig={"maxTokens": MAX_OUTPUT_TOKENS},
    )
    for block in response["output"]["message"]["content"]:
        if "text" in block:
            return block["text"]
    raise ValueError("応答に要約テキストがありません。")


def create_client():
    """Create a Bedrock Runtime client using boto3's standard credential chain."""
    import boto3

    return boto3.Session().client("bedrock-runtime")


def configured_model_id():
    """Return the optional environment override or the exercise default."""
    return os.environ.get("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID)
