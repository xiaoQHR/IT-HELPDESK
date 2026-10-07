import json
import redis.asyncio as redis


from core.config import settings

class MemoryManager:
    """使用redis管理当前会话的工作记忆"""
    def __init__(
            self,
            redis_url:str=settings.redis_url,
            ttl_seconds:int=24*60*60,
            max_messages:int=20,
    ) ->None:
        self.redis=redis.from_url(
            redis_url,
            decode_responses=True,
        )
        self.ttl_seconds=ttl_seconds
        self.max_messages=max_messages
        
    @staticmethod
    def _build_key(user_id:str,conv_id:str)->str:
        """生成当前会话在 Redis 中的键。"""
        return f"wm:{user_id}:{conv_id}"

    async def add_message(
            self,
            user_id:str,
            conv_id:str,
            role:str,
            content:str,
    )->None:
        """向指定会话追加一条消息。"""
        if role not in {"user","assistant"}:
            raise ValueError(
                "role 必须是 user 或 assistant"
            )

        key=self._build_key(user_id,conv_id)

        message={
            "role":role,
            "content":content,
        }

        serialized_message=json.dumps(
            message,
            ensure_ascii=False,
        )

        async with self.redis.pipeline(
            transaction=True
        ) as pipe:
            pipe.rpush(key,serialized_message)
            pipe.ltrim(key,-self.max_messages,-1)
            pipe.expire(key,self.ttl_seconds)
            await pipe.execute()

    async def get_messages(
            self,
            user_id:str,
            conv_id:str,
    )-> list[dict[str,str]]:
        """按时间顺序读取指定会话的消息。"""

        key=self._build_key(user_id,conv_id)
        raw_messages=await(self.redis.lrange(key,0,-1))

        return [
            json.loads(raw_message)
            for raw_message in raw_messages
        ]
    async def clear_conversation(
        self,
            user_id:str,
            conv_id:str,
    )->None:
        """删除指定会话的全部工作记忆。"""
        key=self._build_key(user_id,conv_id)
        await self.redis.delete(key)

    async def close(self)->None:
        """关闭redis客户端连接"""
        await self.redis.aclose()