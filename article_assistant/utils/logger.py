#
# Created by Renatus Madrigal on 12/28/2025
#

import os
import sys
from typing import Callable, Optional
import logging
from loguru import logger

from mcp.types import LoggingMessageNotificationParams


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the logging call was made
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # type: ignore[union-attr]
            frame = frame.f_back  # type: ignore[union-attr]
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logger(log_level: Optional[str] = None, redirect_std: bool = False) -> None:
    """
    Sets up the logger with the specified log level.

    Args:
        log_level (str): The logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
    """
    logger.remove()  # Remove default logger

    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{module}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
    )

    if redirect_std:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.root.addHandler(InterceptHandler())
        logging.root.setLevel(log_level)


def get_mcp_logger(prefix: str = "") -> Callable:
    async def mcp_log_handler(params: LoggingMessageNotificationParams):
        level = params.level.upper()
        # depth=2 means skip 2 frames: mcp_log_handler itself and this wrapper
        logger.opt(depth=2).log(level, f"{prefix}{params.data}")

    return mcp_log_handler
