"""Ask one question from the command line and display the response."""

from bedrock_chat import configure_console, converse_turn, create_client


def main():
    configure_console()
    question = input("質問を入力してください: ").strip()
    if not question:
        print("質問が空のため終了します。")
        return 0

    answer = converse_turn(create_client(), [], question)
    print(f"Bedrock: {answer}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
