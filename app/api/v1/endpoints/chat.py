"""
对话端点。
"""

import logging
import json
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.agents.graph import build_rag_graph
from app.api.deps import QdrantDep, SettingsDep
from app.db.session import get_db
from app.models.chat_session import ChatSession, ChatMessage as DBChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, SourceReference
from app.schemas.common import APIResponse

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


async def _prepare_session_and_messages(request: ChatRequest, settings, db: AsyncSession):
    """提取通用的 session 维护逻辑。确保能从数据库读历史并持久化用户新消息"""
    statement = select(ChatSession).where(ChatSession.id == request.session_id)
    result = await db.execute(statement)
    session_obj = result.scalars().first()
    
    if not session_obj:
        title = request.message[:20] + "..." if len(request.message) > 20 else request.message
        session_obj = ChatSession(id=request.session_id, title=title)
        db.add(session_obj)
        await db.commit()
    else:
        # 更新活跃时间
        session_obj.updated_at = datetime.utcnow()
        db.add(session_obj)
        await db.commit()

    # 从库中倒序取出 max 条记录
    statement = select(DBChatMessage).where(DBChatMessage.session_id == session_obj.id).order_by(DBChatMessage.created_at)
    res = await db.execute(statement)
    db_messages = res.scalars().all()
    
    recent_history = db_messages[-settings.max_chat_history_messages:] if settings.max_chat_history_messages > 0 else db_messages

    langchain_messages = []
    for m in recent_history:
        if m.role == "user":
            langchain_messages.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            langchain_messages.append(AIMessage(content=m.content))
            
    # 追加当前用户的最新提问
    langchain_messages.append(HumanMessage(content=request.message))
    
    # 将用户这一问落库
    user_msg = DBChatMessage(session_id=session_obj.id, role="user", content=request.message)
    db.add(user_msg)
    await db.commit()

    return session_obj, langchain_messages


@router.post(
    "",
    response_model=APIResponse[ChatResponse],
    summary="知识库问答"
)
async def chat(
    request: ChatRequest,
    settings: SettingsDep,
    qdrant: QdrantDep,
    db: AsyncSession = Depends(get_db)
) -> APIResponse[ChatResponse]:
    logger.info("收到对话请求: session=%s, message='%s'", request.session_id, request.message[:50])

    graph = build_rag_graph(settings=settings, qdrant_service=qdrant)
    session_obj, langchain_messages = await _prepare_session_and_messages(request, settings, db)

    initial_state = {
        "messages": langchain_messages,
        "query": request.message,
        "documents": [],
        "generation": "",
        "relevance_scores": [],
        "retry_count": 0,
        "max_retries": 2,
    }

    result = await graph.ainvoke(initial_state)

    sources = [
        SourceReference(content=doc.content[:200], source=doc.source)
        for doc in result.get("documents", [])
    ]
    
    answer_text = result.get("generation", "抱歉，未能生成回答。")

    # 结果落库
    assistant_msg = DBChatMessage(
        session_id=session_obj.id,
        role="assistant",
        content=answer_text,
        sources_json=json.dumps([s.model_dump() for s in sources], ensure_ascii=False)
    )
    db.add(assistant_msg)
    await db.commit()

    return APIResponse(
        data=ChatResponse(
            session_id=session_obj.id,
            answer=answer_text,
            sources=sources,
        ),
    )


@router.post(
    "/stream",
    summary="流式知识库问答"
)
async def chat_stream(
    request: ChatRequest,
    settings: SettingsDep,
    qdrant: QdrantDep,
    db: AsyncSession = Depends(get_db)
):
    logger.info("收到流式对话请求: session=%s, message='%s'", request.session_id, request.message[:50])

    graph = build_rag_graph(settings=settings, qdrant_service=qdrant)
    session_obj, langchain_messages = await _prepare_session_and_messages(request, settings, db)

    initial_state = {
        "messages": langchain_messages,
        "query": request.message,
        "documents": [],
        "generation": "",
        "relevance_scores": [],
        "retry_count": 0,
        "max_retries": 2,
    }

    async def event_generator():
        yield f"event: start\ndata: {json.dumps({'session_id': str(session_obj.id)})}\n\n"
        
        full_answer = ""
        current_sources = []

        async for event in graph.astream_events(initial_state, version="v2"):
            kind = event["event"]
            name = event.get("name")
            
            if kind == "on_chain_end" and name == "retrieve":
                output = event["data"].get("output", {})
                if isinstance(output, dict) and "documents" in output:
                    docs = output["documents"]
                    current_sources = [{"source": d.source, "content": d.content[:200]} for d in docs]
                    yield f"event: sources\ndata: {json.dumps({'sources': current_sources})}\n\n"
            
            # 使用 tags 过滤仅仅在终局生成节点输出
            if kind == "on_chat_model_stream" and "final_node" in event.get("tags", []):
                chunk = event["data"]["chunk"]
                if chunk.content:
                    full_answer += chunk.content
                    yield f"event: message\ndata: {json.dumps({'chunk': chunk.content})}\n\n"

        yield "event: end\ndata: {}\n\n"
        
        # 存库回答落盘
        assistant_msg = DBChatMessage(
            session_id=session_obj.id,
            role="assistant",
            content=full_answer,
            sources_json=json.dumps(current_sources, ensure_ascii=False) if current_sources else None
        )
        db.add(assistant_msg)
        await db.commit()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
