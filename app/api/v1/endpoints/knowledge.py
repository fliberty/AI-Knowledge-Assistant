"""
知识库管理端点。
"""

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile

from app.api.deps import QdrantDep, SettingsDep
from app.data_processing.chunker import DocumentChunker
from app.data_processing.loader import DocumentLoader
from app.schemas.common import APIResponse
from app.schemas.knowledge import (
    DocumentUploadResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    SearchResultItem,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
logger = logging.getLogger(__name__)


@router.post(
    "/upload",
    response_model=APIResponse[DocumentUploadResponse],
    summary="上传知识文档",
)
async def upload_document(
    file: UploadFile,
    settings: SettingsDep,
    qdrant: QdrantDep,
) -> APIResponse[DocumentUploadResponse]:
    """
    上传文档到知识库。

    支持 PDF, TXT, Markdown 格式。文档将被自动分块并存储到向量数据库。
    """
    logger.info("接收文件上传: %s", file.filename)

    # 保存上传文件到临时路径
    suffix = Path(file.filename).suffix if file.filename else ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # 加载 → 分块 → 入库
        documents = DocumentLoader.load(tmp_path)

        # 覆盖 source 为原始文件名
        for doc in documents:
            doc.metadata["source"] = file.filename or "unknown"

        chunker = DocumentChunker(settings)
        chunks = chunker.split(documents)

        ids = await qdrant.add_documents(chunks)

        return APIResponse(
            data=DocumentUploadResponse(
                document_id=ids[0] if ids else "",
                filename=file.filename or "unknown",
                chunk_count=len(chunks),
                status="processed",
            ),
            message=f"成功处理文档，生成 {len(chunks)} 个分块",
        )
    finally:
        # 清理临时文件
        Path(tmp_path).unlink(missing_ok=True)


@router.post(
    "/search",
    response_model=APIResponse[KnowledgeSearchResponse],
    summary="语义搜索",
)
async def search_knowledge(
    request: KnowledgeSearchRequest,
    qdrant: QdrantDep,
) -> APIResponse[KnowledgeSearchResponse]:
    """在知识库中进行语义搜索。"""
    results = await qdrant.similarity_search(
        query=request.query,
        k=request.top_k,
        score_threshold=request.score_threshold,
    )

    items = [
        SearchResultItem(
            content=doc.page_content,
            source=doc.metadata.get("source", "unknown"),
            score=score,
        )
        for doc, score in results
    ]

    return APIResponse(
        data=KnowledgeSearchResponse(
            query=request.query,
            results=items,
            total=len(items),
        ),
    )
