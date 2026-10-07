import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    """IT Helpdesk 运行配置。"""

    anthropic_api_key: str
    anthropic_base_url: str
    anthropic_model: str

    redis_url:str


    chroma_host: str
    chroma_port: int

    embedding_model:str

def load_settings()->Settings:
    """读取并检查运行配置"""
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    base_url = os.getenv("ANTHROPIC_BASE_URL", "").strip()
    model = os.getenv("ANTHROPIC_MODEL", "").strip()

    redis_url=os.getenv("REDIS_URL","").strip()

    chroma_host = os.getenv("CHROMA_HOST", "").strip()
    chroma_port_text = os.getenv("CHROMA_PORT", "").strip()

    embedding_model=os.getenv(
        "EMBEDDING_MODEL",
        "",
    ).strip()

    if not api_key:
        raise RuntimeError("未配置 ANTHROPIC_API_KEY")

    if not model:
        raise RuntimeError("未配置 ANTHROPIC_MODEL")

    if not redis_url:
        raise RuntimeError("未配置REDIS_URL")

    if not chroma_host:
        raise RuntimeError("未配置 CHROMA_HOST")

    if not chroma_port_text:
        raise RuntimeError("未配置 CHROMA_PORT")

    if not embedding_model:
        raise RuntimeError("未配置 EMBEDDING_MODEL")

    try:
        chroma_port=int(chroma_port_text)
    except ValueError as exc:
        raise RuntimeError(
            "CHROMA_PORT必须是整数"
        ) from exc

    return Settings(
        anthropic_api_key=api_key,
        anthropic_base_url=base_url,
        anthropic_model=model,
        redis_url=redis_url,
        chroma_host=chroma_host,
        chroma_port=chroma_port,
        embedding_model=embedding_model,
    )

settings = load_settings()