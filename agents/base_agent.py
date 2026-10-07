from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """所有客服agent的抽象基类"""
    agent_type:str
    system_prompt:str

    @abstractmethod
    async def handle(
            self,
            message: str,
            history: list[dict[str, str]] | None = None,
            knowledge_context: str | None = None,
            request_context: str | None = None,
    ) -> str:
        """根据消息、历史、知识库和请求上下文回答。"""

        raise NotImplementedError