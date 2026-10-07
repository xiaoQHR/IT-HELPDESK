from agents.base_agent import BaseAgent
from core.llm_client import call_llm

class GeneralAgent(BaseAgent):
    """负责普通咨询和初步接待。"""
    agent_type="general"
    system_prompt=(
        "你是 IT Helpdesk 的通用客服。"
        "你负责普通咨询、首次接待和问题澄清。"
        "请准确、简洁、礼貌地回答。"
        "如果信息不足，请向用户询问必要信息。"
        "如果问题明显属于技术故障或账单退款，"
        "请说明需要交给对应的专业客服处理。"
    )

    async def handle(
            self,
            message:str,
            history:list[dict[str,str]] |None=None,
            knowledge_context: str | None = None,
            request_context: str | None = None,
    )->str:
        return await call_llm(
            system_prompt=self.system_prompt,
            user_message=message,
            history=history,
            knowledge_context=knowledge_context,
            request_context=request_context,
        )