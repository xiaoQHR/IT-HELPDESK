import asyncio

from core.llm_client import call_llm


async def main() -> None:
    response = await call_llm(
        system_prompt="你是一个简洁、友好的智能客服助手。",
        user_message="你好，请用一句话介绍你自己。",
    )

    print("Model response:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())