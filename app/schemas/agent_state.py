"""
LangGraph 状态管理模型

定义 RAG Agent 工作流中传递的核心状态结构。
使用 TypedDict 与 Annotated 配合 LangGraph 的状态管理机制。
"""

from typing import Annotated, Any

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# ──────────────────────────────────────────────
# Pydantic 模型 — 用于数据校验和序列化
# ──────────────────────────────────────────────


class RetrievedDocument(BaseModel):
    """检索到的文档片段。"""

    content: str = Field(..., description="文档内容")
    source: str = Field(default="unknown", description="文档来源")
    score: float = Field(default=0.0, description="相似度分数", ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class GradeResult(BaseModel):
    """文档相关性评分结果。"""

    is_relevant: bool = Field(..., description="文档是否与查询相关")
    reasoning: str = Field(default="", description="评分理由")


# ──────────────────────────────────────────────
# LangGraph State — 使用 TypedDict + Annotated
# ──────────────────────────────────────────────


class AgentState(TypedDict):
    """
    LangGraph RAG Agent 核心状态。

    使用 Annotated 类型搭配 reducer 函数，确保消息列表
    在多个节点间正确追加而非覆盖。

    Attributes:
        messages: 对话消息列表（由 add_messages reducer 管理）
        query: 用户原始查询
        documents: 检索到的文档列表
        generation: LLM 生成的回答
        relevance_scores: 文档相关性评分
        retry_count: 当前重试次数
        max_retries: 最大重试次数
    """

    messages: Annotated[list[BaseMessage], add_messages]
    query: str
    documents: list[RetrievedDocument]
    generation: str
    relevance_scores: list[GradeResult]
    retry_count: int
    max_retries: int
