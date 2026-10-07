import asyncio

from agents.technical_agent import TechnicalAgent


async def main() -> None:
    agent = TechnicalAgent()

    response_text = await agent.handle(
        "My application always returns a 401 error when I try to log in."
    )

    print("Agent type:", agent.agent_type)
    print("Technical response:")
    print(response_text)


if __name__ == "__main__":
    asyncio.run(main())