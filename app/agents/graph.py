"""
LangGraph 工作流定义

构建 RAG（Retrieval-Augmented Generation）工作流图。

工作流节点:
    retrieve → grade_documents → [should_retry] → generate
                                      ↓
                                    retry → retrieve (循环)
"""

import logging
from functools import partial

from langgraph.graph import END, StateGraph

from app.agents.rag_agent import generate, grade_documents, retrieve, should_retry, route_query
from app.schemas.agent_state import AgentState
from app.services.llm import get_chat_model
from app.services.vector_store import QdrantService
from app.core.config import Settings

logger = logging.getLogger(__name__)


def build_rag_graph(settings: Settings, qdrant_service: QdrantService) -> StateGraph:
    """
    构建 RAG 工作流图。

    Args:
        settings: 应用配置
        qdrant_service: Qdrant 服务实例

    Returns:
        编译后的 LangGraph StateGraph
    """
    llm = get_chat_model(settings)

    # 使用 partial 绑定外部依赖到节点函数
    retrieve_node = partial(retrieve, qdrant_service=qdrant_service)
    grade_node = partial(grade_documents, llm=llm)
    generate_node = partial(generate, llm=llm)

    # ── 构建图 ──────────────────────────────

    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade_documents", grade_node)
    workflow.add_node("generate", generate_node)

    # 设置基于意图分析的条件入口
    route_node_logic = partial(route_query, llm=llm)
    workflow.set_conditional_entry_point(
        route_node_logic,
        {
            "retrieve": "retrieve",
            "generate": "generate",
        },
    )

    # 添加边
    workflow.add_edge("retrieve", "grade_documents")

    # 条件边：根据评分结果决定是重试还是生成
    workflow.add_conditional_edges(
        "grade_documents",
        should_retry,
        {
            "retry": "retrieve",
            "generate": "generate",
        },
    )

    workflow.add_edge("generate", END)

    logger.info("RAG 工作流图构建完成")

    return workflow.compile()
