from dataclasses import dataclass

from core.intent_recognizer import IntentRecognizer
from core.semantic_intent_recognizer import (
    SemanticIntentRecognizer,
)


@dataclass(frozen=True)
class HybridIntentResult:
    """混合意图识别结果。"""

    intent: str
    confidence: float
    matched_keywords: list[str]
    pattern_intent: str
    semantic_intent: str
    pattern_confidence: float
    semantic_confidence: float
    combined_scores: dict[str, float]




class HybridIntentRecognizer:
    """融合关键词规则与语义向量结果。"""

    INTENTS = (
        "technical",
        "billing",
        "general",
    )

    def __init__(
        self,
        pattern_weight: float = 0.3,
        semantic_weight: float = 0.7,
    ) -> None:
        if pattern_weight < 0:
            raise ValueError(
                "pattern_weight 不能小于 0"
            )

        if semantic_weight < 0:
            raise ValueError(
                "semantic_weight 不能小于 0"
            )

        if pattern_weight + semantic_weight == 0:
            raise ValueError(
                "意图识别权重不能同时为 0"
            )

        total_weight = (
            pattern_weight + semantic_weight
        )

        self.pattern_weight = (
            pattern_weight / total_weight
        )
        self.semantic_weight = (
            semantic_weight / total_weight
        )

        self.pattern_recognizer = (
            IntentRecognizer()
        )

        self.semantic_recognizer = (
            SemanticIntentRecognizer()
        )

    def recognize(
        self,
        message: str,
    ) -> HybridIntentResult:
        """融合两种识别方式的结果。"""

        pattern_result = (
            self.pattern_recognizer.recognize(
                message
            )
        )

        semantic_result = (
            self.semantic_recognizer.recognize(
                message
            )
        )

        pattern_scores = {
            intent: 0.0
            for intent in self.INTENTS
        }

        pattern_scores[
            pattern_result.intent
        ] = pattern_result.confidence

        combined_scores: dict[str, float] = {}

        for intent in self.INTENTS:
            combined_score = (
                self.pattern_weight
                * pattern_scores[intent]
                + self.semantic_weight
                * semantic_result.scores[intent]
            )

            combined_scores[intent] = round(
                combined_score,
                4,
            )

        best_intent = max(
            combined_scores.items(),
            key=lambda item: item[1],
        )[0]

        return HybridIntentResult(
            intent=best_intent,
            confidence=combined_scores[best_intent],
            matched_keywords=(
                pattern_result.matched_keywords
            ),
            pattern_intent=pattern_result.intent,
            semantic_intent=semantic_result.intent,
            pattern_confidence=(
                pattern_result.confidence
            ),
            semantic_confidence=(
                semantic_result.confidence
            ),
            combined_scores=combined_scores,
        )


