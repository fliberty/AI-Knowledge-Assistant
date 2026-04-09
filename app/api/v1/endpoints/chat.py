"""
对话端点。
"""

import logging

from fastapi import APIRouter
from langchain_core.messages import HumanMessage

from app.agents.graph import build_rag_graph
from app.api.deps import QdrantDep, SettingsDep
from app.schemas.chat import ChatRequest, ChatResponse, SourceReference
from app.schemas.common import APIResponse

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=APIResponse[ChatResponse],
    summary="知识库问答",
)
async def chat(
    request: ChatRequest,
    settings: SettingsDep,
    qdrant: QdrantDep,
) -> APIResponse[ChatResponse]:
    """
    基于知识库的智能问答。

    使用 LangGraph RAG 工作流：检索 → 评估 → 生成。
    """
    logger.info("收到对话请求: session=%s, message='%s'", request.session_id, request.message[:50])

    # 构建并执行 RAG 工作流
    graph = build_rag_graph(settings=settings, qdrant_service=qdrant)

    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "query": request.message,
        "documents": [],
        "generation": "",
        "relevance_scores": [],
        "retry_count": 0,
        "max_retries": 2,
    }

    result = await graph.ainvoke(initial_state)

    # 组装响应
    sources = [
        SourceReference(
            content=doc.content[:200],
            source=doc.source,
        )
        for doc in result.get("documents", [])
    ]

    return APIResponse(
        data=ChatResponse(
            session_id=request.session_id,
            answer=result.get("generation", "抱歉，未能生成回答。"),
            sources=sources,
        ),
    )
