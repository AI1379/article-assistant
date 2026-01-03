import asyncio
from collections.abc import AsyncIterable
from datetime import date

import yaml
from loguru import logger
from pydantic_ai import (
    Agent,
    AgentStreamEvent,
    FinalResultEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    PartStartEvent,
    RunContext,
    TextPart,
    TextPartDelta,
    ThinkingPart,
    ThinkingPartDelta,
    ToolCallPart,
    ToolCallPartDelta,
)
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.mcp import MCPServerStdio
from mcp.types import LoggingMessageNotificationParams

from article_assistant.agents import (
    ArchitectDeps,
    ScriberDeps,
    create_architect_agent,
    create_scriber_agent,
    create_stylist_agent,
)
from article_assistant.config import Config
from article_assistant.tools import (
    KnowledgeBase,
    StructureManager,
    StyleManager,
    get_base_tools,
)
from article_assistant.utils.logger import (
    setup_logger,
    InterceptHandler,
    get_mcp_logger,
)

from article_assistant.workflows.generate_article import generate_article_workflow


async def main2():
    config_file = "config.yaml"
    with open(config_file, "r") as file:
        config_dict = yaml.safe_load(file)
    config = Config(**config_dict)
    logger.info(f"Loaded config: {config}")

    ddg_mcp = MCPServerStdio(
        "uvx",
        args=["duckduckgo-mcp-server"],
        timeout=30000,
        log_handler=get_mcp_logger(prefix="[DDG MCP] "),
    )

    model = OpenAIChatModel(
        config.llm.model_name,
        provider=OpenAIProvider(
            api_key=config.llm.api_key, base_url=config.llm.base_url
        ),
    )

    article = await generate_article_workflow(
        model=model,
        topic="The benefits of AI in healthcare",
        target_language="Simplified Chinese",
        target_audience="medical professionals",
        toolsets=[ddg_mcp],
    )

    print("\n--- Final Article Output ---\n")
    print(article)

    with open("output.md", "w", encoding="utf-8") as f:
        f.write(article)


if __name__ == "__main__":
    setup_logger("TRACE")
    asyncio.run(main2())
