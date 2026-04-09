"""
文档加载器

支持多格式文档加载（PDF, TXT, Markdown），
使用 LangChain 和 Unstructured 生态。
"""

import logging
from pathlib import Path

from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# 支持的文件扩展名 → 加载函数映射
_SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown"}


class DocumentLoader:
    """
    多格式文档加载器。

    支持:
        - PDF (通过 unstructured)
        - TXT / Markdown (直接读取)
    """

    @staticmethod
    def load(file_path: str | Path) -> list[Document]:
        """
        加载单个文档。

        Args:
            file_path: 文件路径

        Returns:
            LangChain Document 列表

        Raises:
            ValueError: 不支持的文件格式
            FileNotFoundError: 文件不存在
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")

        ext = path.suffix.lower()
        if ext not in _SUPPORTED_EXTENSIONS:
            raise ValueError(f"不支持的文件格式: {ext}  (支持: {_SUPPORTED_EXTENSIONS})")

        logger.info("加载文档: %s (格式: %s)", path.name, ext)

        if ext == ".pdf":
            return DocumentLoader._load_pdf(path)
        else:
            return DocumentLoader._load_text(path)

    @staticmethod
    def _load_pdf(path: Path) -> list[Document]:
        """加载 PDF 文件。"""
        from langchain_community.document_loaders import UnstructuredFileLoader

        loader = UnstructuredFileLoader(str(path), strategy="fast")
        documents = loader.load()

        # 注入来源元数据
        for doc in documents:
            doc.metadata["source"] = path.name
            doc.metadata["file_type"] = "pdf"

        logger.info("PDF 加载完成: %s, 共 %d 个片段", path.name, len(documents))
        return documents

    @staticmethod
    def _load_text(path: Path) -> list[Document]:
        """加载文本 / Markdown 文件。"""
        content = path.read_text(encoding="utf-8")

        doc = Document(
            page_content=content,
            metadata={
                "source": path.name,
                "file_type": path.suffix.lstrip("."),
            },
        )

        logger.info("文本文件加载完成: %s", path.name)
        return [doc]

    @staticmethod
    def load_directory(dir_path: str | Path) -> list[Document]:
        """
        递归加载目录下所有支持格式的文档。

        Args:
            dir_path: 目录路径

        Returns:
            所有文档的 Document 列表
        """
        directory = Path(dir_path)
        if not directory.is_dir():
            raise NotADirectoryError(f"路径不是目录: {directory}")

        all_documents: list[Document] = []

        for ext in _SUPPORTED_EXTENSIONS:
            for file_path in directory.rglob(f"*{ext}"):
                try:
                    docs = DocumentLoader.load(file_path)
                    all_documents.extend(docs)
                except Exception as e:
                    logger.warning("加载文件失败: %s — %s", file_path, e)

        logger.info("目录加载完成: %s, 共 %d 个文档", directory, len(all_documents))
        return all_documents
