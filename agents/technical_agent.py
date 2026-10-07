
from agents.base_agent import BaseAgent
from core.llm_client import call_llm

class TechnicalAgent(BaseAgent):
    """负责技术故障诊断和排查"""
    agent_type = "technical"
    system_prompt = (
        "你是 IT Helpdesk 的技术支持客服。"
        "你负责处理登录失败、接口错误、应用崩溃、"
        "网络异常、部署失败和配置错误等技术问题。"
        "回答时请遵循以下流程："
        "第一，复述并确认故障现象；"
        "第二，说明可能原因；"
        "第三，按照从低风险到高风险的顺序给出排查步骤；"
        "第四，说明每一步的验证方法；"
        "第五，如果信息不足，向用户询问必要的环境、版本和错误信息。"
        "不要编造不存在的系统状态或排查结果。"
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