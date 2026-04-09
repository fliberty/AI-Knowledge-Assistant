"""
RAG Agent 节点函数

定义 LangGraph 工作流中各节点的具体逻辑：
- retrieve: 文档检索
- grade_documents: 文档相关性评估
- generate: 基于检索内容生成回答
"""

import logging

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.schemas.agent_state import AgentState, GradeResult, RetrievedDocument
from app.services.vector_store import QdrantService

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Prompt 模板
# ──────────────────────────────────────────────

GRADER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个文档相关性评估专家。判断检索到的文档片段是否与用户查询相关。\n"
            "只回答 'yes' 或 'no'。",
        ),
        (
            "human",
            "用户查询: {query}\n\n文档内容: {document}\n\n该文档是否与查询相关?",
        ),
    ]
)

GENERATOR_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个专业的知识库助手。基于以下检索到的文档内容回答用户问题。\n"
            "如果文档中没有相关信息，请如实说明。回答要准确、简洁，并注明信息来源。\n\n"
            "参考文档:\n{context}",
        ),
        ("human", "{query}"),
    ]
)

ROUTER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个智能路由专家。分析用户查询，判断是否需要从外部知识库检索相关信息。\n"
            "如果用户的意图是日常问候（如：你好、谢谢）、基础认知交流、或是指代上一轮对话等，不需要查询专门的文档，请回答 'generate'。\n"
            "如果是询问特定的概念、技术细节、规范、或需要特定知识才能回答的专业问题，请回答 'retrieve'。\n"
            "仅返回 'generate' 或 'retrieve'，不包含其他任何字符。",
        ),
        ("human", "{query}"),
    ]
)


# ──────────────────────────────────────────────
# 节点函数
# ──────────────────────────────────────────────

async def route_query(state: AgentState, *, llm) -> str:
    """
    条件边路由：判断是否需要执行知识库检索。
    """
    query = state["query"]
    logger.info("执行意图分析: query='%s'", query)
    
    chain = ROUTER_PROMPT | llm | StrOutputParser()
    result = await chain.ainvoke({"query": query})
    route = result.strip().lower()
    
    if "retrieve" in route:
        logger.info("👉 意图分析结果: 需要查库 (retrieve)")
        return "retrieve"
        
    logger.info("👉 意图分析结果: 无需查库直接生成 (generate)")
    return "generate"



# ──────────────────────────────────────────────
# 节点函数
# ──────────────────────────────────────────────


async def retrieve(state: AgentState, *, qdrant_service: QdrantService) -> dict:
    """
    检索节点：从向量数据库中检索与查询相关的文档。

    Args:
        state: 当前 Agent 状态
        qdrant_service: Qdrant 服务实例

    Returns:
        更新后的状态字段
    """
    query = state["query"]
    logger.info("执行文档检索: query='%s'", query)

    results = await qdrant_service.similarity_search(query=query, k=5)

    documents = [
        RetrievedDocument(
            content=doc.page_content,
            source=doc.metadata.get("source", "unknown"),
            score=score,
            metadata=doc.metadata,
        )
        for doc, score in results
    ]

    logger.info("检索到 %d 个文档", len(documents))

    return {
        "documents": documents,
        "messages": [AIMessage(content=f"已检索到 {len(documents)} 个相关文档片段。")],
        "retry_count": state.get("retry_count", 0) + 1,
    }


async def grade_documents(state: AgentState, *, llm) -> dict:
    """
    评分节点：评估检索到的文档与查询的相关性。

    Args:
        state: 当前 Agent 状态
        llm: Chat LLM 实例

    Returns:
        更新后的状态字段（过滤后的文档和评分）
    """
    query = state["query"]
    documents = state["documents"]
    logger.info("评估 %d 个文档的相关性", len(documents))

    chain = GRADER_PROMPT | llm | StrOutputParser()
    relevance_scores: list[GradeResult] = []
    relevant_docs: list[RetrievedDocument] = []

    for doc in documents:
        result = await chain.ainvoke({"query": query, "document": doc.content})
        is_relevant = result.strip().lower() == "yes"
        grade = GradeResult(is_relevant=is_relevant, reasoning=result.strip())
        relevance_scores.append(grade)

        if is_relevant:
            relevant_docs.append(doc)

    logger.info("相关文档: %d/%d", len(relevant_docs), len(documents))

    return {
        "documents": relevant_docs,
        "relevance_scores": relevance_scores,
    }


async def generate(state: AgentState, *, llm) -> dict:
    """
    生成节点：基于检索到的文档内容生成回答。

    Args:
        state: 当前 Agent 状态
        llm: Chat LLM 实例

    Returns:
        更新后的状态字段（生成的回答）
    """
    query = state["query"]
    documents = state["documents"]
    logger.info("生成回答: query='%s', docs=%d", query, len(documents))

    # 拼接上下文
    context = "\n\n---\n\n".join(
        f"[来源: {doc.source}]\n{doc.content}" for doc in documents
    )

    if not context:
        context = "（未找到相关文档）"

    chain = GENERATOR_PROMPT | llm | StrOutputParser()
    generation = await chain.ainvoke(
        {"context": context, "query": query},
        config={"tags": ["final_node"]}
    )

    return {
        "generation": generation,
        "messages": [AIMessage(content=generation)],
    }


def should_retry(state: AgentState) -> str:
    """
    条件边：判断是否需要重试检索。

    Returns:
        "retry" 或 "generate"
    """
    relevant_docs = state.get("documents", [])
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    if not relevant_docs and retry_count < max_retries:
        logger.info("未找到相关文档，准备重试 (%d/%d)", retry_count + 1, max_retries)
        return "retry"

    return "generate"
