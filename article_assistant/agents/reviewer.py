#
# Created by Renatus Madrigal on 12/28/2025
#

from dataclasses import dataclass

from pydantic_ai import Agent, Tool
from pydantic_ai.models import Model

from article_assistant.tools import KnowledgeBase, StructureManager, StyleManager


@dataclass
class ReviewerDeps:
    structure_manager: StructureManager
    style_manager: StyleManager
    knowledge_base: KnowledgeBase


def create_reviewer_agent(
    model: str | Model,
    additional_tools: list[Tool] = [],
    **kwargs,
) -> Agent[ReviewerDeps, str]:
    """
    Creates a Reviewer agent with the necessary tools.
    Args:
        model (str | Model): The language model to use for the agent.
        additional_tools (list[Tool]): Additional tools to include in the agent.
    Returns:
        Agent: The created Reviewer agent.
    """
    tools = (
        additional_tools
        + KnowledgeBase.get_tools(attr_name="knowledge_base")
        + StyleManager.get_tools(attr_name="style_manager")
        + StructureManager.get_tools(attr_name="structure_manager")
    )
    system_prompt = (
        "You are an expert article reviewer. Your role is to review and make modifications on article sections "
        "based on the provided outlines, style guides, and knowledge base. "
        "You are also supposed to create a title and keywords for the article based on the content. "
        "Utilize the StyleManager, KnowledgeBase, StructureManager and any other tools to ensure the content is "
        "well-structured, stylistically consistent, and factually accurate. "
    )
    return Agent(
        model,
        deps_type=ReviewerDeps,
        tools=tools,
        system_prompt=system_prompt,
        output_type=str,
        **kwargs,
    )
