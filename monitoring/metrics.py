from prometheus_client import Counter, Histogram


CHAT_REQUESTS_TOTAL = Counter(
    "it_helpdesk_chat_requests_total",
    "IT Helpdesk 聊天请求总数",
    [
        "status",
        "intent",
        "agent_type",
        "knowledge_used",
    ],
)
CHAT_REQUEST_LATENCY_SECONDS = Histogram(
    "it_helpdesk_chat_request_latency_seconds",
    "IT Helpdesk 聊天请求处理耗时",
    [
        "status",
        "agent_type",
    ],
    buckets=(
        0.1,
        0.5,
        1.0,
        2.0,
        5.0,
        10.0,
        30.0,
        60.0,
    ),
)


def record_chat_success(
    intent: str,
    agent_type: str,
    knowledge_used: bool,
    latency_ms: float,
) -> None:
    """记录一次成功的聊天请求。"""

    CHAT_REQUESTS_TOTAL.labels(
        status="success",
        intent=intent,
        agent_type=agent_type,
        knowledge_used=str(
            knowledge_used
        ).lower(),
    ).inc()

    CHAT_REQUEST_LATENCY_SECONDS.labels(
        status="success",
        agent_type=agent_type,
    ).observe(
        latency_ms / 1000
    )


def record_chat_failure(
    latency_ms: float,
) -> None:
    """记录一次失败的聊天请求。"""

    CHAT_REQUESTS_TOTAL.labels(
        status="failure",
        intent="unknown",
        agent_type="unknown",
        knowledge_used="false",
    ).inc()

    CHAT_REQUEST_LATENCY_SECONDS.labels(
        status="failure",
        agent_type="unknown",
    ).observe(
        latency_ms / 1000
    )