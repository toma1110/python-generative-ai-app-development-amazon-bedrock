"""Run a CLI chat, optionally sending earlier turns to the model."""

import argparse

from bedrock_chat import configure_console, converse_turn, create_client


def chat(client, include_history=True, input_fn=input, output_fn=print):
    history = []
    output_fn("質問を入力してください。/exit で終了します。")
    while True:
        try:
            user_text = input_fn("あなた: ").strip()
        except (EOFError, KeyboardInterrupt):
            output_fn("入力を終了しました。")
            return 0

        if user_text.lower() in {"/exit", "/quit"}:
            output_fn("チャットを終了します。")
            return 0
        if not user_text:
            continue

        answer = converse_turn(client, history, user_text, include_history=include_history)
        output_fn(f"Bedrock: {answer}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Amazon BedrockとのCLIチャット")
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="各質問だけを送信し、以前の会話を送信しない",
    )
    args = parser.parse_args(argv)
    configure_console()
    return chat(create_client(), include_history=not args.no_history)


if __name__ == "__main__":
    raise SystemExit(main())
