from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query,File,UploadFile
from pydantic import BaseModel, Field

from fastapi.responses import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)

from monitoring.metrics import (
    record_chat_failure,
    record_chat_success,
)
from agents.agent_orchestrator import AgentOrchestrator
from mcp.tool_manager import tool_manager
from memory.conversation_memory import MemoryManager

from core.document_loader import (
    DEFAULT_MAX_BYTES,
    load_text_document,
)

import time
import logging

orchestrator = AgentOrchestrator()
memory = MemoryManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """管理应用启动和关闭时的资源。"""

    yield

    await memory.close()


logger = logging.getLogger("it_helpdesk.api")

app = FastAPI(
    title="IT Helpdesk",
    description="从零实现的智能客服系统",
    version="0.4.0",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    """聊天接口的请求结构。"""

    message: str = Field(
        min_length=1,
        max_length=2000,
    )
    user_id: str = "anonymous"
    conv_id: str | None = None


class ChatResponse(BaseModel):
    """聊天接口的响应结构。"""

    conv_id: str
    response: str
    intent: str
    intent_confidence: float
    matched_keywords: list[str]
    agent_type: str
    history_message_count: int
    knowledge_used: bool
    knowledge_sources: list[str]
    request_id:str
    latency_ms:float
    pattern_intent: str | None = None
    semantic_intent: str | None = None

    intent_source_scores: dict[str, float] = Field(
        default_factory=dict
    )

    intent_scores: dict[str, float] = Field(
        default_factory=dict
    )

    entities: dict[str, list[str]] = Field(
        default_factory=dict
    )

    required_fields_complete: bool = True

    missing_fields: list[str] = Field(
        default_factory=list
    )

    missing_field_labels: list[str] = Field(
        default_factory=list
    )

    escalated: bool = False
    escalation_reason: str | None = None
    escalation_priority: str = "normal"


class SearchResultResponse(BaseModel):
    """单条知识库检索结果。"""

    document_id: str
    title: str
    content: str
    score: float


class SearchResponse(BaseModel):
    """知识库检索响应。"""

    query: str
    total: int
    results: list[SearchResultResponse]


class KnowledgeDocumentRequest(BaseModel):
    """待写入知识库的文档"""
    title:str=Field(
        min_length=1,
        max_length=200,
    )
    content:str=Field(
        min_length=1,
        max_length=20000,
    )

class AddKnowledgeRequest(BaseModel):
    """批量添加知识库文档的请求"""

    documents:list[KnowledgeDocumentRequest]=Field(
        min_length=1,
        # 每次添加最多100篇
        max_length=100,
    )

class AddKnowledgeResponse(BaseModel):
    """添加知识库文档的结果"""
    processed_documents:int
    processed_chunks:int
    chunk_ids:list[str]
    total_documents:int
    total_chunks:int

class KnowledgeStatsResponse(BaseModel):
    """知识库统计信息"""
    total_documents:int
    total_chunks:int


class KnowledgeDocumentResponse(BaseModel):
    """但拍案知识库文档的信息"""
    source_id:str
    title:str
    chunk_count:int

class KnowledgeDocumentListResponse(BaseModel):
    """知识库文档列表响应"""
    total:int
    documents:list[KnowledgeDocumentResponse]

class DeleteKnowledgeResponse(BaseModel):
    """删除知识库文档的响应"""
    source_id:str
    deleted_chunks:int
    total_documents:int
    total_chunks:int



@app.get("/health")
async def health() -> dict[str, str]:
    """检查 HTTP 服务是否正常运行。"""

    return {
        "status": "ok",
        "service": "IT Helpdesk",
    }

@app.get(
    "/metrics",
    include_in_schema=False,
)
async def metrics() -> Response:
    """返回 Prometheus 格式的监控指标。"""

    return Response(
        content=generate_latest(),
        headers={
            "Content-Type": CONTENT_TYPE_LATEST,
        },
    )


@app.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
) -> ChatResponse:
    """读取记忆，调用 Agent，并保存本轮对话。"""

    conv_id = request.conv_id or uuid4().hex
    request_id=uuid4().hex[:8]
    started_at=time.perf_counter()


    logger.info(
        "chat_request_started"
        "request_id=%s conv_id=%s user_id=%s",
        request_id,
        conv_id,
        request.user_id,
    )


    try:
        history = await memory.get_messages(
            user_id=request.user_id,
            conv_id=conv_id,
        )

        result = await orchestrator.handle(
            message=request.message,
            history=history,
        )

        await memory.add_message(
            user_id=request.user_id,
            conv_id=conv_id,
            role="user",
            content=request.message,
        )
        latency_ms=round(
            (time.perf_counter()-started_at)*1000,
            2,
        )
        record_chat_success(
            intent=result.intent,
            agent_type=result.agent_type,
            knowledge_used=result.knowledge_used,
            latency_ms=latency_ms,
        )
        logger.info(
            "chat_request_completed "
            "request_id=%s conv_id=%s "
            "intent=%s agent_type=%s "
            "knowledge_used=%s latency_ms=%s",
            request_id,
            conv_id,
            result.intent,
            result.agent_type,
            result.knowledge_used,
            latency_ms,
        )
        await memory.add_message(
            user_id=request.user_id,
            conv_id=conv_id,
            role="assistant",
            content=result.response,
        )

    except Exception as exc:
        failed_latency_ms=round(
            (time.perf_counter() - started_at)* 1000,
            2,
        )
        record_chat_failure(
            latency_ms=failed_latency_ms,
        )
        logger.exception(
            "chat_request_failed "
            "request_id=%s conv_id=%s "
            "latency_ms=%s",
            request_id,
            conv_id,
            failed_latency_ms,
        )
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Agent 执行失败",
                "request_id": request_id,
            },
        ) from exc

    return ChatResponse(
        conv_id=conv_id,
        response=result.response,
        intent=result.intent,
        intent_confidence=result.confidence,
        matched_keywords=result.matched_keywords,
        agent_type=result.agent_type,
        history_message_count=len(history),
        knowledge_used=result.knowledge_used,
        knowledge_sources=result.knowledge_sources,
        latency_ms=latency_ms,
        request_id=request_id,
        pattern_intent=result.pattern_intent,
        semantic_intent=result.semantic_intent,
        intent_source_scores=(
            result.intent_source_scores
        ),
        intent_scores=result.intent_scores,

        entities=result.entities,
        required_fields_complete=(
            result.required_fields_complete
        ),
        missing_fields=result.missing_fields,
        missing_field_labels=(
            result.missing_field_labels
        ),
        escalated=result.escalated,
        escalation_reason=result.escalation_reason,
        escalation_priority=result.escalation_priority,

    )


@app.post(
    "/search",
    response_model=SearchResponse,
)
async def search_knowledge(
    query: str = Query(
        ...,
        min_length=1,
        max_length=500,
    ),
    top_k: int = Query(
        default=3,
        ge=1,
        le=20,
    ),
) -> SearchResponse:
    """直接执行知识库语义检索。"""

    try:
        results = (
            await tool_manager.search_knowledge_base(
                query=query,
                top_k=top_k,
                min_score=0.5,
            )
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"知识库检索失败：{exc}",
        ) from exc

    return SearchResponse(
        query=query,
        total=len(results),
        results=[
            SearchResultResponse(
                document_id=result.document_id,
                title=result.title,
                content=result.content,
                score=result.score,
            )
            for result in results
        ],
    )

@app.post(
    "/knowledge/add",
    response_model=AddKnowledgeResponse,
)
async def add_knowledge(
    request:AddKnowledgeRequest,
) -> AddKnowledgeResponse:
    """批量添加或更新知识库文档"""
    documents=[
        {
            "title":document.title,
            "content":document.content,
        }
        for document in request.documents
    ]
    try:
        chunks_ids=(
            await tool_manager.add_knowledge_documents(
                documents
            )
        )
        stats=await tool_manager.get_knowledge_stats()

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )from exc

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"知识库写入失败：{exc}",
        )from exc

    return AddKnowledgeResponse(
        processed_documents=len(documents),
        processed_chunks=len(chunks_ids),
        chunk_ids=chunks_ids,
        total_documents=stats["total_documents"],
        total_chunks=stats["total_chunks"],
    )


@app.post(
    "/knowledge/upload",
    response_model=AddKnowledgeResponse,
)
async def upload_knowledge(
        file:UploadFile=File(...),
)->AddKnowledgeResponse:
    """上传文本文件并写入知识库"""
    try:
# 只读取“最大限制 + 1”字节。
# 如果文件过大，读取结果就会超过限制，
# document_loader 会拒绝该文件。
        data=await file.read(
            DEFAULT_MAX_BYTES+1
        )
        title,content=load_text_document(
            filename=file.filename or "",
            data=data,
        )

        chunk_ids=(
            await tool_manager.add_knowledge_documents(
                [
                    {
                        "title":title,
                        "content":content,
                    }
                ]
            )
        )
        stats=await tool_manager.get_knowledge_stats()

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )from exc

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"知识库文件导入失败：{exc}",
        )from exc
    finally:
        await file.close()

    return AddKnowledgeResponse(
        processed_documents=1,
        processed_chunks=len(chunk_ids),
        chunk_ids=chunk_ids,
        total_documents=stats["total_documents"],
        total_chunks=stats["total_chunks"],
    )


@app.get(
    "/knowledge/stats",
    response_model=KnowledgeStatsResponse,
)
async def get_knowledge_stats() -> KnowledgeStatsResponse:
    """返回知识库原始文档数量和向量切片数"""
    try:
        stats=await tool_manager.get_knowledge_stats()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"知识库统计失败：{exc}",
        )from exc

    return KnowledgeStatsResponse(
        total_documents=stats["total_documents"],
        total_chunks=stats["total_chunks"]
    )

@app.get(
    "/knowledge/documents",
    response_model=KnowledgeDocumentListResponse,
)
async def list_knowledge_documents(

)->KnowledgeDocumentListResponse:
    """返回知识库中的原始文档列表"""
    try:
        documents=(
            await tool_manager.list_knowledge_documents()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"获取知识库文档列表失败：{exc}",
        )from exc
    return KnowledgeDocumentListResponse(
        total=len(documents),
        documents=[
            KnowledgeDocumentResponse(
                source_id=str(document["source_id"]),
                title=str(document["title"]),
                chunk_count=int(
                    document["chunk_count"]
                ),
            )
            for document in documents
        ],
    )

@app.delete(
    "/knowledge/documents/{source_id}",
    response_model=DeleteKnowledgeResponse,
)
async def delete_knowledge_documents(
        source_id:str,
)->DeleteKnowledgeResponse:
    """根据source_id删除整篇文档极其全部切片"""

    try:
        deleted_chunks=(
            await tool_manager.delete_knowledge_document(
                source_id
            )
        )
        stats=await tool_manager.get_knowledge_stats()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )from exc

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"删除知识库文档失败：{exc}",
        )from exc

    if deleted_chunks==0:
        raise HTTPException(
            status_code=404,
            detail="未找到对应的知识库文档"
        )
    return DeleteKnowledgeResponse(
        source_id=source_id,
        deleted_chunks=deleted_chunks,
        total_documents=stats["total_documents"],
        total_chunks=stats["total_chunks"],
    )

