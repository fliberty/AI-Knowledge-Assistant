"""
LLM 服务封装

提供 Chat Model 和 Embedding Model 的工厂函数。
"""

import logging

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.config import Settings

logger = logging.getLogger(__name__)


def get_chat_model(settings: Settings) -> ChatOpenAI:
    """
    创建 Chat LLM 实例。

    Args:
        settings: 应用配置

    Returns:
        ChatOpenAI 实例
    """
    logger.info("初始化 Chat 模型: %s (base_url=%s)", settings.openai_model_name, settings.openai_base_url)

    kwargs: dict = {
        "model": settings.openai_model_name,
        "openai_api_key": settings.openai_api_key,
        "temperature": 0,
        "streaming": True,
    }
    if settings.openai_base_url:
        kwargs["openai_api_base"] = settings.openai_base_url

    return ChatOpenAI(**kwargs)


def get_embeddings(settings: Settings) -> OpenAIEmbeddings:
    """
    创建 Embedding 模型实例。

    Args:
        settings: 应用配置

    Returns:
        OpenAIEmbeddings 实例
    """
    logger.info("初始化 Embedding 模型: %s", settings.openai_embedding_model)

    kwargs: dict = {
        "model": settings.openai_embedding_model,
        "openai_api_key": settings.openai_api_key,
    }
    if settings.openai_base_url:
        kwargs["openai_api_base"] = settings.openai_base_url

    return OpenAIEmbeddings(**kwargs)

