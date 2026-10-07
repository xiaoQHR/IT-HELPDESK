from core.intent_recognizer import IntentRecognizer


recognizer = IntentRecognizer()

test_messages = [
    "应用登录时提示 401 错误",
    "我这个月被重复扣款了",
    "你们提供哪些服务",
]

for message in test_messages:
    result = recognizer.recognize(message)

    print("-" * 50)
    print("Message:", message)
    print("Intent:", result.intent)
    print("Confidence:", result.confidence)
    print("Matched keywords:", result.matched_keywords)