import pytest
from fastapi.testclient import TestClient
from agents.agent_orchestrator import OrchestratorResult

import api.main as main_module
import logging

@pytest.fixture(scope="module")
def client() -> TestClient:
    """启动测试版 FastAPI 客户端。"""

    with TestClient(main_module.app) as test_client:
        yield test_client


def test_health_endpoint(
    client: TestClient,
) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "IT Helpdesk",
    }


def test_chat_rejects_empty_message(
    client: TestClient,
) -> None:
    response = client.post(
        "/chat",
        json={
            "message": "",
            "user_id": "test-user",
            "conv_id": "test-conversation",
        },
    )

    assert response.status_code == 422


def test_list_knowledge_documents_endpoint(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_list_documents(
    ) -> list[dict[str, str | int]]:
        return [
            {
                "source_id": "source-1",
                "title": "退款政策",
                "chunk_count": 2,
            }
        ]

    monkeypatch.setattr(
        main_module.tool_manager,
        "list_knowledge_documents",
        fake_list_documents,
    )

    response = client.get(
        "/knowledge/documents"
    )

    assert response.status_code == 200
    assert response.json() == {
        "total": 1,
        "documents": [
            {
                "source_id": "source-1",
                "title": "退款政策",
                "chunk_count": 2,
            }
        ],
    }


def test_knowledge_stats_endpoint(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_get_stats(
    ) -> dict[str, int]:
        return {
            "total_documents": 6,
            "total_chunks": 9,
        }

    monkeypatch.setattr(
        main_module.tool_manager,
        "get_knowledge_stats",
        fake_get_stats,
    )

    response = client.get(
        "/knowledge/stats"
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_documents": 6,
        "total_chunks": 9,
    }


def test_upload_rejects_unsupported_file(
    client: TestClient,
) -> None:
    response = client.post(
        "/knowledge/upload",
        files={
            "file": (
                "image.png",
                b"fake-image-data",
                "image/png",
            )
        },
    )

    assert response.status_code == 400
    assert "暂不支持" in response.json()["detail"]


def test_delete_unknown_document_returns_404(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_delete_document(
        source_id: str,
    ) -> int:
        return 0

    async def fake_get_stats(
    ) -> dict[str, int]:
        return {
            "total_documents": 6,
            "total_chunks": 9,
        }

    monkeypatch.setattr(
        main_module.tool_manager,
        "delete_knowledge_document",
        fake_delete_document,
    )

    monkeypatch.setattr(
        main_module.tool_manager,
        "get_knowledge_stats",
        fake_get_stats,
    )

    response = client.delete(
        "/knowledge/documents/not-exists"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "未找到对应的知识库文档"
    }


def test_delete_document_returns_updated_stats(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_delete_document(
        source_id: str,
    ) -> int:
        assert source_id == "source-123"
        return 4

    async def fake_get_stats(
    ) -> dict[str, int]:
        return {
            "total_documents": 5,
            "total_chunks": 5,
        }

    monkeypatch.setattr(
        main_module.tool_manager,
        "delete_knowledge_document",
        fake_delete_document,
    )

    monkeypatch.setattr(
        main_module.tool_manager,
        "get_knowledge_stats",
        fake_get_stats,
    )

    response = client.delete(
        "/knowledge/documents/source-123"
    )

    assert response.status_code == 200
    assert response.json() == {
        "source_id": "source-123",
        "deleted_chunks": 4,
        "total_documents": 5,
        "total_chunks": 5,
    }

def test_chat_success_response(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saved_messages: list[dict[str, str]] = []

    async def fake_get_messages(
        user_id: str,
        conv_id: str,
    ) -> list[dict[str, str]]:
        assert user_id == "test-user"
        assert conv_id == "test-conversation"

        return []


    async def fake_add_message(
        user_id: str,
        conv_id: str,
        role: str,
        content: str,
    ) -> None:
        saved_messages.append(
            {
                "user_id": user_id,
                "conv_id": conv_id,
                "role": role,
                "content": content,
            }
        )


    async def fake_orchestrator_handle(
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> OrchestratorResult:
        assert message == "退款多久到账？"
        assert history == []

        return OrchestratorResult(
            response="支付宝退款通常需要一至三个工作日。",
            intent="billing",
            confidence=0.7,
            matched_keywords=["退款"],
            agent_type="billing",
            knowledge_used=True,
            knowledge_sources=["退款政策"],
        )


    monkeypatch.setattr(
        main_module.memory,
        "get_messages",
        fake_get_messages,
    )

    monkeypatch.setattr(
        main_module.memory,
        "add_message",
        fake_add_message,
    )

    monkeypatch.setattr(
        main_module.orchestrator,
        "handle",
        fake_orchestrator_handle,
    )

    response = client.post(
        "/chat",
        json={
            "message": "退款多久到账？",
            "user_id": "test-user",
            "conv_id": "test-conversation",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["conv_id"] == (
        "test-conversation"
    )
    assert len(response_data["request_id"]) == 8
    assert response_data["response"] == (
        "支付宝退款通常需要一至三个工作日。"
    )
    assert response_data["intent"] == "billing"
    assert response_data["intent_confidence"] == 0.7
    assert response_data["agent_type"] == "billing"
    assert response_data["history_message_count"] == 0
    assert response_data["knowledge_used"] is True
    assert response_data["knowledge_sources"] == [
        "退款政策"
    ]
    assert response_data["latency_ms"] >= 0

    assert len(saved_messages) == 2

    assert saved_messages[0]["role"] == "user"
    assert saved_messages[0]["content"] == (
        "退款多久到账？"
    )

    assert saved_messages[1]["role"] == "assistant"
    assert saved_messages[1]["content"] == (
        "支付宝退款通常需要一至三个工作日。"
    )

def test_chat_failure_returns_request_id(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    async def fake_get_messages(
        user_id: str,
        conv_id: str,
    ) -> list[dict[str, str]]:
        return []


    async def fake_orchestrator_handle(
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> None:
        raise RuntimeError(
            "内部测试错误：不应该返回给客户端"
        )


    monkeypatch.setattr(
        main_module.memory,
        "get_messages",
        fake_get_messages,
    )

    monkeypatch.setattr(
        main_module.orchestrator,
        "handle",
        fake_orchestrator_handle,
    )

    with caplog.at_level(
        logging.ERROR,
        logger="it_helpdesk.api",
    ):
        response = client.post(
            "/chat",
            json={
                "message": "测试失败场景",
                "user_id": "test-user",
                "conv_id": "failure-test",
            },
        )

    assert response.status_code == 502

    detail = response.json()["detail"]

    assert detail["message"] == "Agent 执行失败"
    assert len(detail["request_id"]) == 8

    # 内部异常不应该泄露到客户端响应。
    assert "内部测试错误" not in response.text

    # 完整错误应该保留在服务端日志中。
    assert "chat_request_failed" in caplog.text
    assert "内部测试错误" in caplog.text


def test_metrics_endpoint(
    client: TestClient,
) -> None:
    response = client.get("/metrics")

    assert response.status_code == 200

    content_type = response.headers[
        "content-type"
    ]

    assert content_type.startswith("text/plain")

    metrics_text = response.text

    assert (
        "it_helpdesk_chat_requests_total"
        in metrics_text
    )

    assert (
        "it_helpdesk_chat_request_latency_seconds"
        in metrics_text
    )