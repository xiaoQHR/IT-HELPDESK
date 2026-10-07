import asyncio

from memory.conversation_memory import MemoryManager


async def main() -> None:
    memory = MemoryManager()

    user_id = "memory_user"
    conv_id = "memory_session"

    try:
        # 防止上一次测试的数据影响本次结果
        await memory.clear_conversation(
            user_id=user_id,
            conv_id=conv_id,
        )

        # 模拟一轮用户与客服对话
        await memory.add_message(
            user_id=user_id,
            conv_id=conv_id,
            role="user",
            content="我的订单号是 A123456。",
        )

        await memory.add_message(
            user_id=user_id,
            conv_id=conv_id,
            role="assistant",
            content="已经记录您的订单号。",
        )

        # 读取当前会话的全部消息
        messages = await memory.get_messages(
            user_id=user_id,
            conv_id=conv_id,
        )

        print("Messages:")
        for message in messages:
            print(
                f"{message['role']}: "
                f"{message['content']}"
            )

        # 清除会话并再次读取
        await memory.clear_conversation(
            user_id=user_id,
            conv_id=conv_id,
        )

        messages_after_clear = await memory.get_messages(
            user_id=user_id,
            conv_id=conv_id,
        )

        print("Messages after clear:")
        print(messages_after_clear)

    finally:
        await memory.close()


if __name__ == "__main__":
    asyncio.run(main())