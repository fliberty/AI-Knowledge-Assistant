"""
Qdrant 向量数据库服务

封装 Qdrant 客户端操作，提供文档存储与语义搜索能力。
"""

import logging
from uuid import uuid4

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams

from app.core.config import Settings

logger = logging.getLogger(__name__)


class QdrantService:
    """Qdrant 向量数据库服务。"""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: QdrantClient | None = None
        self._vector_store: QdrantVectorStore | None = None
        self._embeddings: OpenAIEmbeddings | None = None

    # ── 生命周期 ──────────────────────────────

    async def initialize(self) -> None:
        """初始化客户端连接和 Embedding 模型。"""
        logger.info(
            "正在连接 Qdrant: %s:%s",
            self._settings.qdrant_host,
            self._settings.qdrant_port,
        )

        self._client = QdrantClient(
            host=self._settings.qdrant_host,
            port=self._settings.qdrant_port,
            api_key=self._settings.qdrant_api_key or None,
        )

        embedding_kwargs: dict = {
            "model": self._settings.openai_embedding_model,
            "openai_api_key": self._settings.openai_api_key,
        }
        if self._settings.openai_base_url:
            embedding_kwargs["openai_api_base"] = self._settings.openai_base_url

        self._embeddings = OpenAIEmbeddings(**embedding_kwargs)

        await self._ensure_collection()

        self._vector_store = QdrantVectorStore(
            client=self._client,
            collection_name=self._settings.qdrant_collection_name,
            embedding=self._embeddings,
        )

        logger.info("Qdrant 服务初始化完成")

    async def close(self) -> None:
        """关闭客户端连接。"""
        if self._client:
            self._client.close()
            logger.info("Qdrant 连接已关闭")

    # ── 集合管理 ──────────────────────────────

    async def _ensure_collection(self) -> None:
        """确保目标集合存在，不存在则创建。"""
        collection_name = self._settings.qdrant_collection_name

        try:
            self._client.get_collection(collection_name)
            logger.info("集合已存在: %s", collection_name)
        except (UnexpectedResponse, Exception):
            logger.info("创建集合: %s", collection_name)
            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=1536,  # text-embedding-3-small 维度
                    distance=Distance.COSINE,
                ),
            )

    # ── 文档操作 ──────────────────────────────

    async def add_documents(self, documents: list[Document]) -> list[str]:
        """
        将文档添加到向量数据库。

        Args:
            documents: LangChain Document 列表

        Returns:
            文档 ID 列表
        """
        if not self._vector_store:
            raise RuntimeError("QdrantService 未初始化，请先调用 initialize()")

        ids = [str(uuid4()) for _ in documents]
        self._vector_store.add_documents(documents=documents, ids=ids)
        logger.info("成功添加 %d 个文档到集合", len(documents))
        return ids

    async def similarity_search(
        self,
        query: str,
        k: int = 2,
        score_threshold: float = 0.7,
    ) -> list[tuple[Document, float]]:
        """
        语义相似度搜索。

        Args:
            query: 搜索查询
            k: 返回结果数量
            score_threshold: 最低相似度阈值

        Returns:
            (Document, score) 元组列表
        """
        if not self._vector_store:
            raise RuntimeError("QdrantService 未初始化，请先调用 initialize()")

        results = self._vector_store.similarity_search_with_score(query=query, k=k)

        # 过滤低于阈值的结果
        filtered = [(doc, score) for doc, score in results if score >= score_threshold]
        logger.info("搜索查询='%s' 返回 %d/%d 条结果 (阈值=%.2f)", query, len(filtered), len(results), score_threshold)
        return filtered

    async def delete_collection(self, collection_name: str | None = None) -> None:
        """删除指定集合。"""
        if not self._client:
            raise RuntimeError("QdrantService 未初始化")

        name = collection_name or self._settings.qdrant_collection_name
        self._client.delete_collection(name)
        logger.info("已删除集合: %s", name)
