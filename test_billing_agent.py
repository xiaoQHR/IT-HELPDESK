import asyncio

from agents.billing_agent import BillingAgent


async def main() -> None:
    agent = BillingAgent()

    response_text = await agent.handle(
        "我这个月被重复扣款了，请直接帮我退款。"
    )

    print("Agent type:", agent.agent_type)
    print("Billing response:")
    print(response_text)


if __name__ == "__main__":
    asyncio.run(main())