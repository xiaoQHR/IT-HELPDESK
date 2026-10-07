from dataclasses import dataclass


@dataclass(frozen=True)
class EscalationDecision:
    """人工升级决策。"""

    escalated: bool
    reason: str | None = None
    priority: str = "normal"


class EscalationPolicy:
    """判断请求是否需要升级到人工客服。"""

    SECURITY_KEYWORDS = (
        "账号被盗",
        "账户被盗",
        "资金损失",
        "未经授权",
        "隐私泄露",
        "信息泄露",
    )

    HUMAN_KEYWORDS = (
        "转人工",
        "人工客服",
        "找人工",
        "真人客服",
        "我要投诉",
        "投诉客服",
    )

    def __init__(
        self,
        low_confidence_threshold: float = 0.3,
    ) -> None:
        self.low_confidence_threshold = (
            low_confidence_threshold
        )

    def evaluate(
        self,
        message: str,
        intent_confidence: float,
    ) -> EscalationDecision:
        """根据消息和意图置信度判断是否升级。"""

        normalized_message = message.strip().lower()

        security_matches = [
            keyword
            for keyword in self.SECURITY_KEYWORDS
            if keyword in normalized_message
        ]

        if security_matches:
            return EscalationDecision(
                escalated=True,
                reason="security_risk",
                priority="high",
            )

        human_matches = [
            keyword
            for keyword in self.HUMAN_KEYWORDS
            if keyword in normalized_message
        ]

        if human_matches:
            return EscalationDecision(
                escalated=True,
                reason="explicit_human_request",
                priority="normal",
            )

        if (
            intent_confidence
            < self.low_confidence_threshold
        ):
            return EscalationDecision(
                escalated=True,
                reason="low_intent_confidence",
                priority="normal",
            )

        return EscalationDecision(
            escalated=False,
        )


escalation_policy = EscalationPolicy()