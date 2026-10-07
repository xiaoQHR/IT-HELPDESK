from dataclasses import dataclass

from core.embedding_service import embedding_service


@dataclass(frozen=True)
class SemanticIntentResult:
    """语义意图识别结果。"""

    intent: str
    confidence: float
    scores: dict[str, float]


class SemanticIntentRecognizer:
    """基于语义向量相似度识别用户意图。"""

    INTENT_EXAMPLES = {
        "technical": [
            "无法登录账号",
            "收不到登录验证码",
            "页面加载失败一直转圈",
            "应用打不开或者崩溃",
            "接口请求超时或返回错误码",
            "部署后出现网络连接问题",
        ],
        "billing": [
            "账户被收取了两笔费用",
            "如何申请退款",
            "取消下一个周期的订阅费用",
            "支付金额存在问题",
            "如何申请发票或开票",
            "自动续费怎么关闭",
        ],
        "general": [
            "介绍一下你们提供的服务",
            "产品有哪些功能",
            "API 套餐包含哪些功能",
            "付款后如何查看物流",
            "会员可以享受哪些权益",
            "你好，我想了解产品",
        ],
    }

    def __init__(
        self,
        general_threshold: float = 0.35,
    ) -> None:
        self.general_threshold = general_threshold

        self._examples: list[tuple[str, str]] = []
        self._example_vectors: list[list[float]] | None = (
            None
        )

        for intent, examples in (
            self.INTENT_EXAMPLES.items()
        ):
            for example in examples:
                self._examples.append(
                    (intent, example)
                )

    def _ensure_example_vectors(self) -> None:
        """首次使用时生成示例向量并缓存。"""

        if self._example_vectors is not None:
            return

        texts = [
            example
            for _, example in self._examples
        ]

        self._example_vectors = (
            embedding_service.encode(texts)
        )

    @staticmethod
    def _cosine_similarity(
        left: list[float],
        right: list[float],
    ) -> float:
        """
        计算余弦相似度。

        当前向量已经归一化，因此点积就是余弦相似度。
        """

        return sum(
            float(left_value) * float(right_value)
            for left_value, right_value
            in zip(left, right)
        )

    def recognize(
        self,
        message: str,
    ) -> SemanticIntentResult:
        """根据语义相似度识别意图。"""

        message = message.strip()

        if not message:
            raise ValueError("message 不能为空")

        self._ensure_example_vectors()

        if self._example_vectors is None:
            raise RuntimeError("意图示例向量加载失败")

        query_vector = embedding_service.encode_one(
            message
        )

        scores = {
            "technical": 0.0,
            "billing": 0.0,
            "general": 0.0,
        }

        for (
            (intent, _),
            example_vector,
        ) in zip(
            self._examples,
            self._example_vectors,
        ):
            similarity = self._cosine_similarity(
                query_vector,
                example_vector,
            )

            scores[intent] = max(
                scores[intent],
                similarity,
            )

        best_intent = max(
            scores,
            key=scores.get,
        )

        best_score = scores[best_intent]

        if best_score < self.general_threshold:
            best_intent = "general"

        rounded_scores = {
            intent: round(score, 4)
            for intent, score in scores.items()
        }

        return SemanticIntentResult(
            intent=best_intent,
            confidence=round(best_score, 4),
            scores=rounded_scores,
        )