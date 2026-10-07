import logging
from dataclasses import dataclass, field


from agents.base_agent import BaseAgent
from agents.billing_agent import BillingAgent
from agents.general_agent import GeneralAgent
from agents.technical_agent import TechnicalAgent
from core.hybrid_intent_recognizer import (
    HybridIntentRecognizer,
)
from mcp.tool_manager import tool_manager

from core.entity_extractor import entity_extractor
from core.required_field_checker import (
    required_field_checker,
)
from agents.escalation_agent import EscalationAgent
from core.escalation_policy import escalation_policy

logger=logging.getLogger(__name__)

@dataclass(frozen=True)
class OrchestratorResult:
    """Agent 编排器的执行结果。"""

    response: str
    intent: str
    confidence: float
    matched_keywords: list[str]
    agent_type: str
    knowledge_used: bool
    knowledge_sources: list[str]

    pattern_intent: str | None = None
    semantic_intent: str | None = None

    intent_source_scores: dict[str, float] = field(
        default_factory=dict
    )

    intent_scores: dict[str, float] = field(
        default_factory=dict
    )

    entities: dict[str, list[str]] = field(
        default_factory=dict
    )

    required_fields_complete: bool = True

    missing_fields: list[str] = field(
        default_factory=list
    )

    missing_field_labels: list[str] = field(
        default_factory=list
    )

    escalated: bool = False
    escalation_reason: str | None = None
    escalation_priority: str = "normal"


class AgentOrchestrator:
    """识别用户意图，并将请求路由给对应的 Agent。"""
    def __init__(self) -> None:
        self.intent_recognizer=HybridIntentRecognizer()

        self.agents:dict[str,BaseAgent]={
            "general":GeneralAgent(),
            "technical":TechnicalAgent(),
            "billing":BillingAgent(),
            "escalation": EscalationAgent(),
        }
    #     agent注册表

    async def handle(
            self,
            message: str,
            history: list[dict[str, str]] | None = None,
    ) -> OrchestratorResult:
        """识别意图、抽取实体并调用对应 Agent。"""

        # 每条消息只进行一次混合意图识别。
        intent_result = (
            self.intent_recognizer.recognize(message)
        )

        escalation_decision = escalation_policy.evaluate(
            message=message,
            intent_confidence=intent_result.confidence,
        )

        # 实体抽取与意图识别彼此独立。
        entities = entity_extractor.extract(message)
        error_code_context: str | None = None

        if (
            intent_result.intent == "technical"
            and entities.error_code
        ):
            error_code_result = (
                await tool_manager.lookup_error_code(
                    entities.error_code[0]
                )
            )

            if error_code_result is not None:
                suggestions = "\n".join(
                    f"- {suggestion}"
                    for suggestion
                    in error_code_result.suggestions
                )

                error_code_context = (
                    "系统错误码工具查询结果：\n"
                    f"错误码：{error_code_result.code}\n"
                    f"名称：{error_code_result.name}\n"
                    f"含义：{error_code_result.description}\n"
                    "建议：\n"
                    f"{suggestions}\n"
                    "回答时应以该查询结果为准，"
                    "但不要声称已经完成实际排查。"
                )

        required_field_result = (
            required_field_checker.check(
                intent=intent_result.intent,
                entities=entities.to_dict(),
            )
        )

        request_context: str | None = None

        if escalation_decision.escalated:
            escalation_context = (
                "当前请求已触发人工升级。"
                f"升级原因：{escalation_decision.reason}；"
                f"优先级：{escalation_decision.priority}。"
                "请生成清晰的人工交接摘要，"
                "但不要声称已经创建工单。"
            )

            if request_context:
                request_context = (
                    f"{request_context}\n"
                    f"{escalation_context}"
                )
            else:
                request_context = escalation_context


        if intent_result.intent == "billing":
            if required_field_result.complete:
                request_context = (
                    "账单业务所需的订单号、时间和金额"
                    "已经提供完整。"
                    "不要重复询问这些字段，"
                    "请直接根据现有信息说明下一步处理方式。"
                )
            else:
                missing_labels = "、".join(
                    required_field_result.missing_field_labels
                )

                request_context = (
                    "系统字段检查显示，当前账单问题仍缺少："
                    f"{missing_labels}。"
                    "只询问这些缺失信息，"
                    "不要重复询问用户已经提供的信息。"
                )

        # 根据最终融合意图选择 Agent。
        # agent = self.agents.get(
        #     intent_result.intent,
        #     self.agents["general"],
        # )
        if escalation_decision.escalated:
            agent = self.agents["escalation"]
        else:
            agent = self.agents.get(
                intent_result.intent,
                self.agents["general"],
            )

        knowledge_results = []

        try:
            knowledge_results = (
                await tool_manager.search_knowledge_base(
                    query=message,
                    top_k=3,
                    min_score=0.5,
                )
            )

        except Exception:
            logger.exception(
                "知识库检索失败，降级为无知识库回答"
            )

        knowledge_context = (
            tool_manager.format_knowledge_context(
                knowledge_results
            )
        )

        if error_code_context:
            if request_context:
                request_context = (
                    f"{request_context}\n\n"
                    f"{error_code_context}"
                )
            else:
                request_context = error_code_context

        response_text = await agent.handle(
            message=message,
            history=history,
            knowledge_context=(
                knowledge_context
                if knowledge_context
                else None
            ),
            request_context=request_context,
        )

        return OrchestratorResult(
            response=response_text,
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            matched_keywords=(
                intent_result.matched_keywords
            ),
            agent_type=agent.agent_type,
            knowledge_used=bool(knowledge_results),
            knowledge_sources=[
                result.title
                for result in knowledge_results
            ],
            pattern_intent=(
                intent_result.pattern_intent
            ),
            semantic_intent=(
                intent_result.semantic_intent
            ),
            intent_source_scores={
                "pattern": (
                    intent_result.pattern_confidence
                ),
                "embedding": (
                    intent_result.semantic_confidence
                ),
            },
            intent_scores=(
                intent_result.combined_scores
            ),
            entities=entities.to_dict(),
            required_fields_complete=(
                required_field_result.complete
            ),
            missing_fields=(
                required_field_result.missing_fields
            ),
            missing_field_labels=(
                required_field_result.missing_field_labels
            ),
            escalated=escalation_decision.escalated,
            escalation_reason=(
                escalation_decision.reason
            ),
            escalation_priority=(
                escalation_decision.priority
            ),
        )