#
# Created by Renatus Madrigal on 12/26/2025
#

from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import (
    Agent,
    Tool,
    PromptedOutput,
    ToolOutput,
    NativeOutput,
)
from pydantic_ai.models import Model

from article_assistant.tools import StructureManager
from article_assistant.types import OutlineItem, Outline


@dataclass
class ArchitectDeps:
    structure_manager: StructureManager


def create_architect_agent(
    model: str | Model,
    additional_tools: list[Tool] = [],
    target_language: str = "English",
    **kwargs,
) -> Agent[ArchitectDeps, Outline]:
    """
    Creates an Architect agent with the necessary tools.
    Args:
        model (str | Model): The language model to use for the agent.
        additional_tools (list[Tool]): Additional tools to include in the agent.
    Returns:
        Agent: The created Architect agent.
    """
    system_prompt = (
        "You are an expert article architect. Your role is to design the structure of articles, "
        "including creating detailed outlines and section plans based on given topics and requirements. "
        "You are supposed to include introduction as the first and conclusion as the last sections in the outlines you create. "
        "Utilize the StructureManager to manage and organize article structures effectively."
        f"Ensure all outputs are in {target_language}."
    )
    return Agent(
        model,
        deps_type=ArchitectDeps,
        tools=additional_tools,
        system_prompt=system_prompt,
        output_type=Outline,
        **kwargs,
    )
