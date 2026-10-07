from agents.base_agent import BaseAgent
from core.llm_client import call_llm


class EscalationAgent(BaseAgent):
    """负责人工升级和交接摘要。"""

    agent_type = "escalation"

    system_prompt = (
        "你是 IT Helpdesk 的人工升级与交接客服。"
        "你的职责是确认升级原因、整理已知信息、"
        "标记优先级，并生成简洁的人工交接摘要。"
        "回答时遵循以下规则："
        "第一，明确告知用户该问题建议由人工客服继续处理；"
        "第二，概括用户的问题和系统已经识别出的信息；"
        "第三，指出仍然缺少的信息；"
        "第四，高风险安全问题应提醒用户立即修改密码、"
        "冻结相关支付方式或保护账号；"
        "第五，不要声称已经创建工单、联系人工或完成退款，"
        "除非工具返回了明确结果；"
        "第六，不要要求用户提供密码、验证码、"
        "完整银行卡号或完整访问令牌。"
    )

    async def handle(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
        knowledge_context: str | None = None,
        request_context: str | None = None,
    ) -> str:
        return await call_llm(
            system_prompt=self.system_prompt,
            user_message=message,
            history=history,
            knowledge_context=knowledge_context,
            request_context=request_context,
        )