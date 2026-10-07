from core.semantic_intent_recognizer import (
    SemanticIntentRecognizer,
)


def main() -> None:
    recognizer = SemanticIntentRecognizer()

    messages = [
        "验证码一直收不到，没法进入账号",
        "页面一直转圈，怎么都打不开",
        "钱被收了两次",
        "我不想继续用了，怎么取消下个月的费用",
        "API 套餐有哪些功能",
    ]

    for message in messages:
        result = recognizer.recognize(message)

        print("-" * 60)
        print("Message:", message)
        print("Intent:", result.intent)
        print("Confidence:", result.confidence)
        print("Scores:", result.scores)


if __name__ == "__main__":
    main()