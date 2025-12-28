#
# Created by Renatus Madrigal on 12/28/2025
#

import os
import sys
from typing import Optional

from loguru import logger


def setup_logger(log_level: Optional[str] = None) -> None:
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
