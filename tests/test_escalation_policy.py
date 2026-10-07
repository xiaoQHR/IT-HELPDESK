from core.escalation_policy import EscalationPolicy


def test_security_issue_uses_high_priority() -> None:
    policy = EscalationPolicy()

    decision = policy.evaluate(
        message="我的账号被盗了，请转人工处理。",
        intent_confidence=0.9,
    )

    assert decision.escalated is True
    assert decision.reason == "security_risk"
    assert decision.priority == "high"


def test_explicit_human_request_escalates() -> None:
    policy = EscalationPolicy()

    decision = policy.evaluate(
        message="这个问题请帮我转人工客服。",
        intent_confidence=0.9,
    )

    assert decision.escalated is True
    assert decision.reason == (
        "explicit_human_request"
    )
    assert decision.priority == "normal"


def test_low_confidence_escalates() -> None:
    policy = EscalationPolicy(
        low_confidence_threshold=0.3
    )

    decision = policy.evaluate(
        message="我也不知道该怎么描述",
        intent_confidence=0.2,
    )

    assert decision.escalated is True
    assert decision.reason == (
        "low_intent_confidence"
    )


def test_normal_request_does_not_escalate() -> None:
    policy = EscalationPolicy()

    decision = policy.evaluate(
        message="退款多久到账？",
        intent_confidence=0.8,
    )

    assert decision.escalated is False
    assert decision.reason is None
    assert decision.priority == "normal"