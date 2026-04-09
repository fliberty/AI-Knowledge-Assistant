"""Knowledge base schemas."""

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Document upload response."""

    document_id: str = Field(...)
    filename: str = Field(...)
    chunk_count: int = Field(...)
    status: str = Field(default="processed")


class KnowledgeSearchRequest(BaseModel):
    """Semantic search request."""

    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class SearchResultItem(BaseModel):
    """A single search result item."""

    content: str = Field(...)
    source: str = Field(...)
    score: float = Field(...)


class KnowledgeSearchResponse(BaseModel):
    """Semantic search response."""

    query: str = Field(...)
    results: list[SearchResultItem] = Field(default_factory=list)
    total: int = Field(default=0)


class KnowledgeStatsResponse(BaseModel):
    """Knowledge base status summary."""

    status: str = Field(default="ready")
    collection_name: str = Field(...)
    chunk_count: int = Field(default=0)
    embedding_model: str = Field(...)
    vector_store_available: bool = Field(default=True)
    message: str | None = Field(default=None)
