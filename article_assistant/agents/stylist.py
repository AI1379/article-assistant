#
# Created by Renatus Madrigal on 12/26/2025
#

from article_assistant.types import StyleGuide
from pydantic_ai import Agent, Tool, PromptedOutput
from pydantic_ai.models import Model


def create_stylist_agent(
    model: str | Model,
    additional_tools: list[Tool] = [],
    target_language: str = "English",
    **kwargs,
) -> Agent[None, StyleGuide]:
    """
    Creates a Stylist agent with the necessary tools.
    Args:
        model (str | Model): The language model to use for the agent.
        additional_tools (list[Tool]): Additional tools to include in the agent.
    Returns:
        Agent: The created Stylist agent.
    """
    # TODO: Human-in-the-loop for style decisions
    system_prompt = (
        "You are an expert article stylist. Your role is to define and manage the style of articles, "
        "including setting tone, voice, and target audience based on given requirements. "
        f"Ensure all outputs are in {target_language}."
    )
    return Agent(
        model,
        tools=additional_tools,
        system_prompt=system_prompt,
        output_type=PromptedOutput(
            [StyleGuide], name="StyleGuide", description="The article style guide"
        ),
        **kwargs,
    )
