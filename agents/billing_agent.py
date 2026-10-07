

from agents.base_agent import BaseAgent
from core.llm_client import call_llm

class BillingAgent(BaseAgent):
    """负责账单、支付、退款和发票问题。"""
    agent_type = "billing"
    system_prompt = (
        "你是 IT Helpdesk 的账单客服。"
        "你负责处理退款、重复扣款、支付失败、"
        "订阅续费、账单金额和发票等问题。"
        "回答时请遵循以下流程："
        "第一，确认用户具体遇到的账单场景；"
        "第二，收集处理问题所需的订单号、支付时间、"
        "支付渠道和金额等必要信息；"
        "第三，解释可能原因和标准处理流程；"
        "第四，说明用户可以执行的下一步操作；"
        "第五，信息不足时先询问，不要直接下结论。"
        "不要声称已经查询、退款或修改了真实账单，"
        "除非工具返回了明确的执行结果。"
        "不要要求用户提供完整银行卡号、密码、"
        "短信验证码或支付密钥。"
    )
    async def handle(
            self,
            message:str,
            history: list[dict[str, str]] | None = None,
            knowledge_context: str | None = None,
            request_context: str | None = None,
    ) ->str:
        return await call_llm(
            system_prompt=self.system_prompt,
            user_message=message,
            history=history,
            knowledge_context=knowledge_context,
            request_context=request_context,
        )