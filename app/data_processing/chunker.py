"""
文档分块器

基于 LangChain RecursiveCharacterTextSplitter 实现文档分块，
支持可配置的块大小和重叠。
"""

import logging

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import Settings

logger = logging.getLogger(__name__)


class DocumentChunker:
    """
    文档分块器。

    使用递归字符分割策略，按语义边界（段落 → 句子 → 单词）
    将长文档拆分为可嵌入的小块。
    """

    def __init__(self, settings: Settings) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", ".", " ", ""],
            is_separator_regex=False,
        )

    def split(self, documents: list[Document]) -> list[Document]:
        """
        将文档列表拆分为小块。

        Args:
            documents: 原始文档列表

        Returns:
            分块后的文档列表，保留原始元数据
        """
        chunks = self._splitter.split_documents(documents)

        # 为每个块添加序号元数据
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i

        logger.info(
            "文档分块完成: %d 个文档 → %d 个块 (chunk_size=%d, overlap=%d)",
            len(documents),
            len(chunks),
            self._splitter._chunk_size,
            self._splitter._chunk_overlap,
        )

        return chunks
