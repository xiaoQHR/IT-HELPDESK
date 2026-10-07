import asyncio

from agents.agent_orchestrator import AgentOrchestrator


async def main() -> None:
    orchestrator = AgentOrchestrator()

    message = "应用登录时提示 401 错误"

    result = await orchestrator.handle(message)

    print("Message:", message)
    print("Intent:", result.intent)
    print("Confidence:", result.confidence)
    print("Matched keywords:", result.matched_keywords)
    print("Agent type:", result.agent_type)
    print("Response:")
    print(
        "Knowledge used:",
        result.knowledge_used,
    )
    print(
        "Knowledge sources:",
        result.knowledge_sources,
    )
    print(result.response)


if __name__ == "__main__":
    asyncio.run(main())