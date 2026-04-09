"""
结构化日志配置模块

提供 JSON 格式的结构化日志输出，便于生产环境日志采集（ELK / Loki 等）。
"""

import logging
import sys
from datetime import datetime, timezone
from typing import Any

from app.core.config import get_settings


class JSONFormatter(logging.Formatter):
    """JSON 格式日志格式化器。"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info and record.exc_info[1]:
            log_data["exception"] = self.formatException(record.exc_info)

        # 使用标准库 json 序列化避免额外依赖
        import json

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging() -> None:
    """初始化结构化日志系统。"""
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除已有 handler 防止重复
    root_logger.handlers.clear()

    # 控制台 handler — 强制使用 UTF-8 编码，避免 Windows GBK 编码导致 emoji 输出崩溃
    import io
    utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    console_handler = logging.StreamHandler(utf8_stdout)
    console_handler.setLevel(log_level)

    if settings.debug:
        # 开发模式：可读格式
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # 生产模式：JSON 格式
        formatter = JSONFormatter()

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 降低第三方库日志级别
    for noisy_logger in ("httpx", "httpcore", "openai", "urllib3", "asyncio"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    logging.getLogger(__name__).info("日志系统初始化完成 (level=%s, debug=%s)", settings.log_level, settings.debug)


def get_logger(name: str) -> logging.Logger:
    """获取命名日志器。"""
    return logging.getLogger(name)
