import asyncio

from mcp.tool_manager import tool_manager


async def main() -> None:
    results = await tool_manager.search_knowledge_base(
        query="退款多久能到账？",
        top_k=2,
    )

    context = tool_manager.format_knowledge_context(
        results
    )

    print("Search result count:", len(results))
    print()
    print(context)


if __name__ == "__main__":
    asyncio.run(main())