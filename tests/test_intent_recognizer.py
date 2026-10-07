import pytest

from core.intent_recognizer import IntentRecognizer


@pytest.fixture
def recognizer() -> IntentRecognizer:
    """为每个测试提供意图识别器。"""

    return IntentRecognizer()


def test_recognize_technical_intent(
    recognizer: IntentRecognizer,
) -> None:
    result = recognizer.recognize(
        "应用登录时提示 401 错误"
    )

    assert result.intent == "technical"
    assert result.confidence == pytest.approx(0.9)
    assert set(result.matched_keywords) == {
        "登录",
        "401",
        "错误",
    }


def test_recognize_billing_intent(
    recognizer: IntentRecognizer,
) -> None:
    result = recognizer.recognize(
        "我的订单发生了重复扣款，需要退款"
    )

    assert result.intent == "billing"
    assert result.confidence == pytest.approx(0.8)
    assert set(result.matched_keywords) == {
        "扣款",
        "退款",
    }


def test_unknown_message_uses_general_intent(
    recognizer: IntentRecognizer,
) -> None:
    result = recognizer.recognize(
        "你们可以提供哪些服务？"
    )

    assert result.intent == "general"
    assert result.confidence == pytest.approx(0.5)
    assert result.matched_keywords == []


def test_english_api_keyword_is_case_insensitive(
    recognizer: IntentRecognizer,
) -> None:
    result = recognizer.recognize(
        "My API request timed out"
    )

    assert result.intent == "technical"
    assert "api" in result.matched_keywords


def test_confidence_does_not_exceed_limit(
    recognizer: IntentRecognizer,
) -> None:
    result = recognizer.recognize(
        "登录 API 接口出现网络超时和 401 错误"
    )

    assert result.intent == "technical"
    assert result.confidence <= 0.95