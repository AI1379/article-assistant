#
# Created by Renatus Madrigal on 12/26/2025
#

from pydantic import BaseModel, Field
from pydantic_ai import (
    Agent,
    Tool,
    PromptedOutput,
)
from pydantic_ai.models import Model
from article_assistant.tools import StyleManager, KnowledgeBase, StructureManager
from article_assistant.types import StyleGuide, OutlineItem, Outline, SectionInfo

from dataclasses import dataclass


@dataclass
class ScriberDeps:
    style_manager: StyleManager
    knowledge_base: KnowledgeBase
    structure_manager: StructureManager


def create_scriber_agent(
    model: str | Model,
    additional_tools: list[Tool] = [],
    **kwargs,
) -> Agent[ScriberDeps, SectionInfo]:
    """
    Creates a Scriber agent with the necessary tools.
    Args:
        model (str | Model): The language model to use for the agent.
        tools (list[Tool]): Additional tools to include in the agent.
    Returns:
        Agent: The created Scriber agent.
    """
    tools = (
        additional_tools
        + KnowledgeBase.get_tools(attr_name="knowledge_base")
        + StyleManager.get_tools(attr_name="style_manager")
        + StructureManager.get_tools(attr_name="structure_manager")
    )
    system_prompt = (
        "You are an expert article scriber. Your role is to write detailed sections of articles "
        "based on the provided outlines, style guides, and knowledge base. "
        "Utilize the StyleManager, KnowledgeBase, StructureManager and any other tools to ensure the content is "
        "well-structured, stylistically consistent, and factually accurate. "
        "You are not supposed to add a heading line in the contents you write. "
        "The sub-headings should start from H3. "
        "You are allowed to slightly change your writing style with a little mismatch to the style guide "
        "to make your writing more human-like and less AI-generated, but do not deviate too much from the style guide."
    )
    return Agent(
        model,
        deps_type=ScriberDeps,
        tools=tools,
        system_prompt=system_prompt,
        output_type=SectionInfo,
        **kwargs,
    )
