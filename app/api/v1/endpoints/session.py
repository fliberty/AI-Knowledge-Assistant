import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.chat_session import ChatSession, ChatMessage
from app.schemas.common import APIResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("", response_model=APIResponse[List[dict]])
async def get_sessions(db: AsyncSession = Depends(get_db)):
    """获取按修改时间排序的会话列表，不包含消息实体"""
    statement = select(ChatSession).order_by(desc(ChatSession.updated_at))
    result = await db.execute(statement)
    sessions = result.scalars().all()
    
    data = [
        {"id": str(s.id), "title": s.title, "created_at": s.created_at.isoformat(), "updated_at": s.updated_at.isoformat()}
        for s in sessions
    ]
    return APIResponse(data=data)

@router.get("/{session_id}", response_model=APIResponse[dict])
async def get_session_detail(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """获取单个会话详情（携带所有的对话历史）"""
    statement = select(ChatSession).options(selectinload(ChatSession.messages)).where(ChatSession.id == session_id)
    result = await db.execute(statement)
    session_obj = result.scalars().first()
    
    if not session_obj:
        raise HTTPException(status_code=404, detail="会话不存在")
        
    messages_data = [
        {"id": str(m.id), "role": m.role, "content": m.content, "sources": m.sources_json}
        for m in sorted(session_obj.messages, key=lambda x: x.created_at)
    ]
    
    return APIResponse(data={
        "id": str(session_obj.id),
        "title": session_obj.title,
        "created_at": session_obj.created_at.isoformat(),
        "messages": messages_data
    })

@router.delete("/{session_id}", response_model=APIResponse[bool])
async def delete_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """删除指定的对话记录和所有的子消息。"""
    statement = select(ChatSession).where(ChatSession.id == session_id)
    result = await db.execute(statement)
    session_obj = result.scalars().first()
    
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")
        
    await db.delete(session_obj)
    await db.commit()
    return APIResponse(data=True)
