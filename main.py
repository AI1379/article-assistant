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
from article_assistant.utils.logger import setup_logger

output_messages: list[str] = []
thinking_delta: str = ""
text_delta: str = ""
tool_args_delta: str = ""


async def handle_event(event: AgentStreamEvent):
    global thinking_delta, text_delta, tool_args_delta
    if isinstance(event, PartStartEvent):
        output_messages.append(f"[Request] Starting part {event.index}: {event.part!r}")
        if isinstance(event.part, TextPart):
            text_delta += event.part.content
        elif isinstance(event.part, ThinkingPart):
            thinking_delta += event.part.content or ""
        elif isinstance(event.part, ToolCallPart):
            tool_args_delta += str(event.part.args)
    elif isinstance(event, PartDeltaEvent):
        if isinstance(event.delta, TextPartDelta):
            output_messages.append(
                f"[Request] Part {event.index} text delta: {event.delta.content_delta!r}"
            )
            text_delta += event.delta.content_delta
        elif isinstance(event.delta, ThinkingPartDelta):
            output_messages.append(
                f"[Request] Part {event.index} thinking delta: {event.delta.content_delta!r}"
            )
            thinking_delta += event.delta.content_delta or ""
        elif isinstance(event.delta, ToolCallPartDelta):
            output_messages.append(
                f"[Request] Part {event.index} args delta: {event.delta.args_delta}"
            )
            tool_args_delta += str(event.delta.args_delta)
    elif isinstance(event, FunctionToolCallEvent):
        output_messages.append(
            f"[Tools] The LLM calls tool={event.part.tool_name!r} with args={event.part.args} (tool_call_id={event.part.tool_call_id!r})"
        )
    elif isinstance(event, FunctionToolResultEvent):
        output_messages.append(
            f"[Tools] Tool call {event.tool_call_id!r} returned => {event.result.content}"
        )
    elif isinstance(event, FinalResultEvent):
        output_messages.append(
            f"[Result] The model starting producing a final result (tool_name={event.tool_name})"
        )


async def event_stream_handler(
    ctx: RunContext[object],
    event_stream: AsyncIterable[AgentStreamEvent],
):
    async for event in event_stream:
        await handle_event(event)


async def main():
    config_file = "config.yaml"
    with open(config_file, "r") as file:
        config_dict = yaml.safe_load(file)
    config = Config(**config_dict)
    logger.info(f"Loaded config: {config}")

    model = OpenAIChatModel(
        config.llm.model_name,
        provider=OpenAIProvider(
            api_key=config.llm.api_key, base_url=config.llm.base_url
        ),
    )
    structure_manager = StructureManager()
    architect_agent = create_architect_agent(
        model,
        additional_tools=[],
        target_language="Simplified Chinese",
    )
    # async with architect_agent.run_stream(
    #     "Create a detailed outline for an article about the benefits of AI in healthcare.",
    #     deps=ArchitectDeps(structure_manager=structure_manager),
    #     event_stream_handler=event_stream_handler,
    # ) as stream:
    #     pass

    # return

    result = await architect_agent.run(
        "Create a detailed outline for an article about the benefits of AI in healthcare.",
        deps=ArchitectDeps(structure_manager=structure_manager),
    )

    print(result.output)
    print(type(result.output))

    structure_manager.set_outline(result.output)

    for item in structure_manager.outline.outline_items:
        print(f"Outline Item: {item.title}, Purpose: {item.purpose}")

    stylist = create_stylist_agent(
        model,
        additional_tools=[],
        target_language="Simplified Chinese",
    )

    style_result = await stylist.run(
        (
            "Create a style guide for an article about the benefits of AI in healthcare. "
            "The target audience is medical professionals."
        ),
    )
    print(style_result.output)
    print(type(style_result.output))

    style_manager = StyleManager(style_guide=style_result.output)
    knowledge_base = KnowledgeBase()

    scriber_deps = ScriberDeps(
        style_manager=style_manager,
        knowledge_base=knowledge_base,
        structure_manager=structure_manager,
    )
    scriber_agent = create_scriber_agent(
        model,
        additional_tools=[],
    )

    for idx, outline_item in enumerate(structure_manager.outline.outline_items):
        prompt = (
            f"Write a detailed section for the outline item titled '{outline_item.title}'. "
            f"Purpose: {outline_item.purpose}, Argument: {outline_item.argument}, "
            f"Expected Conclusion: {outline_item.expected_conclusion}, "
            f"Expected Length: {outline_item.expected_length} words."
        )
        section_result = await scriber_agent.run(
            prompt,
            deps=scriber_deps,
        )
        print(f"\n--- Section {idx} Output ---\n")
        print(section_result.output)
        print(f"\n--- End of Section {idx} ---\n")
        # async with scriber_agent.run_stream(
        #     prompt, deps=scriber_deps, event_stream_handler=event_stream_handler
        # ) as stream:
        #     async for section_result in stream.stream_text():
        #         output_messages.append(f"[Scriber Output] {section_result}")


from article_assistant.workflows.generate_article import generate_article_workflow


async def main2():
    config_file = "config.yaml"
    with open(config_file, "r") as file:
        config_dict = yaml.safe_load(file)
    config = Config(**config_dict)
    logger.info(f"Loaded config: {config}")

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
    )

    print("\n--- Final Article Output ---\n")
    print(article)

    with open("output.md", "w", encoding="utf-8") as f:
        f.write(article)


if __name__ == "__main__":
    setup_logger("TRACE")
    asyncio.run(main2())
    # try:
    #     asyncio.run(main())
    # finally:
    #     print("\n--- Event Log ---\n")
    #     for message in output_messages:
    #         print(message)
    #     print(f"\n--- Thinking Delta ---\n{thinking_delta}")
    #     print(f"\n--- Text Delta ---\n{text_delta}")
    #     print(f"\n--- Tool Args Delta ---\n{tool_args_delta}")
