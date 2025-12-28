#
# Created by Renatus Madrigal on 12/28/2025
#

from pydantic_ai import Tool
from loguru import logger


def current_date() -> str:
    """
    Returns the current date as a string.

    Returns:
        str: The current date in YYYY-MM-DD format.
    """
    from datetime import datetime

    logger.trace("Fetching current date.")

    return datetime.now().strftime("%Y-%m-%d")


def get_base_tools() -> list[Tool]:
    """
    Returns a list of base tools for the Article Assistant application.

    Returns:
        list[Tool]: A list of base tools.
    """
    return [
        Tool(
            current_date,
            name="current_date",
            description="Get the current date.",
            takes_ctx=False,
        )
    ]
