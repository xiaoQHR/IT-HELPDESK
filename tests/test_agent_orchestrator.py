import pytest

from agents.agent_orchestrator import AgentOrchestrator
from mcp.knowledge_base import SearchResult
from mcp.tool_manager import tool_manager


@pytest.mark.asyncio
async def test_routes_technical_message_to_technical_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    orchestrator = AgentOrchestrator()

    received: dict[str, object] = {}

    async def fake_search(
        query: str,
        top_k: int,
        min_score: float,
    ) -> list[SearchResult]:
        return []

    async def fake_handle(
        message: str,
        history: list[dict[str, str]] | None = None,
        knowledge_context: str | None = None,
        request_context: str | None = None,
    ) -> str:
        received["message"] = message
        received["history"] = history
        received["knowledge_context"] = knowledge_context

        return "模拟技术客服回答"

    monkeypatch.setattr(
        tool_manager,
        "search_knowledge_base",
        fake_search,
    )

    monkeypatch.setattr(
        orchestrator.agents["technical"],
        "handle",
        fake_handle,
    )

    history = [
        {
            "role": "user",
            "content": "之前登录失败",
        }
    ]

    result = await orchestrator.handle(
        message="应用登录时提示 401 错误",
        history=history,
    )

    assert result.intent == "technical"
    assert result.agent_type == "technical"
    assert result.response == "模拟技术客服回答"
    assert result.knowledge_used is False
    assert result.knowledge_sources == []

    assert received["message"] == (
        "应用登录时提示 401 错误"
    )
    assert received["history"] == history
    assert received["knowledge_context"] is None


@pytest.mark.asyncio
async def test_passes_knowledge_to_billing_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    orchestrator = AgentOrchestrator()

    received: dict[str, object] = {}

    async def fake_search(
        query: str,
        top_k: int,
        min_score: float,
    ) -> list[SearchResult]:
        return [
            SearchResult(
                document_id="refund-doc",
                title="退款政策",
                content=(
                    "支付宝退款通常需要一至三个工作日。"
                ),
                score=0.9,
            )
        ]

    async def fake_handle(
        message: str,
        history: list[dict[str, str]] | None = None,
        knowledge_context: str | None = None,
        request_context: str | None = None,
    ) -> str:
        received["knowledge_context"] = (
            knowledge_context
        )

        return "模拟账单客服回答"

    monkeypatch.setattr(
        tool_manager,
        "search_knowledge_base",
        fake_search,
    )

    monkeypatch.setattr(
        orchestrator.agents["billing"],
        "handle",
        fake_handle,
    )

    result = await orchestrator.handle(
        message="支付宝退款多久到账？",
    )

    assert result.intent == "billing"
    assert result.agent_type == "billing"
    assert result.response == "模拟账单客服回答"
    assert result.knowledge_used is True
    assert result.knowledge_sources == ["退款政策"]

    knowledge_context = received[
        "knowledge_context"
    ]

    assert isinstance(knowledge_context, str)
    assert "退款政策" in knowledge_context
    assert "一至三个工作日" in knowledge_context


@pytest.mark.asyncio
async def test_knowledge_failure_degrades_gracefully(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    orchestrator = AgentOrchestrator()

    received: dict[str, object] = {}

    async def fake_search(
        query: str,
        top_k: int,
        min_score: float,
    ) -> list[SearchResult]:
        raise RuntimeError("ChromaDB unavailable")

    async def fake_handle(
        message: str,
        history: list[dict[str, str]] | None = None,
        knowledge_context: str | None = None,
        request_context: str | None = None,
    ) -> str:
        received["knowledge_context"] = (
            knowledge_context
        )

        return "知识库不可用时的普通回答"

    monkeypatch.setattr(
        tool_manager,
        "search_knowledge_base",
        fake_search,
    )

    monkeypatch.setattr(
        orchestrator.agents["general"],
        "handle",
        fake_handle,
    )

    result = await orchestrator.handle(
        message="你们提供哪些服务？",
    )

    assert result.intent == "general"
    assert result.agent_type == "general"
    assert result.knowledge_used is False
    assert result.knowledge_sources == []
    assert received["knowledge_context"] is None

@pytest.mark.asyncio
async def test_billing_agent_receives_missing_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    orchestrator = AgentOrchestrator()

    received: dict[str, object] = {}

    async def fake_search(
        query: str,
        top_k: int,
        min_score: float,
    ) -> list[SearchResult]:
        return []

    async def fake_handle(
        message: str,
        history: list[dict[str, str]] | None = None,
        knowledge_context: str | None = None,
        request_context: str | None = None,
    ) -> str:
        received["request_context"] = request_context
        return "请补充支付时间和扣款金额。"

    monkeypatch.setattr(
        tool_manager,
        "search_knowledge_base",
        fake_search,
    )

    monkeypatch.setattr(
        orchestrator.agents["billing"],
        "handle",
        fake_handle,
    )

    result = await orchestrator.handle(
        message="订单号 A123456，我被重复扣款了。",
    )

    assert result.intent == "billing"

    assert result.required_fields_complete is False

    assert result.missing_fields == [
        "date",
        "amount",
    ]

    assert result.missing_field_labels == [
        "支付或问题发生时间",
        "支付或扣款金额",
    ]

    request_context = received["request_context"]

    assert isinstance(request_context, str)

    assert "支付或问题发生时间" in request_context
    assert "支付或扣款金额" in request_context

    # 订单号已经提供，不应作为缺失字段再次询问。
    assert "订单号或交易号" not in request_context


@pytest.mark.asyncio
async def test_security_issue_routes_to_escalation_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    orchestrator = AgentOrchestrator()

    received: dict[str, object] = {}

    async def fake_search(
        query: str,
        top_k: int,
        min_score: float,
    ) -> list[SearchResult]:
        return []

    async def fake_handle(
        message: str,
        history: list[dict[str, str]] | None = None,
        knowledge_context: str | None = None,
        request_context: str | None = None,
    ) -> str:
        received["request_context"] = request_context
        return "建议立即升级人工安全支持。"

    monkeypatch.setattr(
        tool_manager,
        "search_knowledge_base",
        fake_search,
    )

    monkeypatch.setattr(
        orchestrator.agents["escalation"],
        "handle",
        fake_handle,
    )

    result = await orchestrator.handle(
        message="我的账号被盗了，请转人工。",
    )

    assert result.escalated is True
    assert result.escalation_reason == (
        "security_risk"
    )
    assert result.escalation_priority == "high"
    assert result.agent_type == "escalation"

    request_context = received["request_context"]

    assert isinstance(request_context, str)
    assert "security_risk" in request_context
    assert "high" in request_context

@pytest.mark.asyncio
async def test_technical_agent_receives_error_code_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    orchestrator = AgentOrchestrator()

    captured: dict[str, object] = {}

    async def fake_handle(
        message: str,
        history: list[dict[str, str]] | None = None,
        knowledge_context: str | None = None,
        request_context: str | None = None,
    ) -> str:
        captured["request_context"] = request_context
        return "模拟技术客服回答"

    async def fake_search(
        query: str,
        top_k: int = 3,
        min_score: float = 0.5,
    ) -> list:
        return []

    monkeypatch.setattr(
        orchestrator.agents["technical"],
        "handle",
        fake_handle,
    )
    monkeypatch.setattr(
        tool_manager,
        "search_knowledge_base",
        fake_search,
    )

    result = await orchestrator.handle(
        "应用登录时提示 401 错误"
    )

    request_context = captured["request_context"]

    assert result.agent_type == "technical"
    assert isinstance(request_context, str)
    assert "401" in request_context
    assert "Unauthorized" in request_context
    assert "请求没有通过身份认证" in request_context