#
# Created by Renatus Madrigal on 12/26/2025
#

from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import RunContext, Tool
from loguru import logger

from article_assistant.types import StyleGuide


class StyleManager(BaseModel):
    """
    Manages the style of articles within the Article Assistant application.
    """

    style_guide: StyleGuide = Field(
        default=StyleGuide(),
        description="The style guide for the article, represented as a StyleGuide object.",
    )

    def set_style_guide(self, style_guide: StyleGuide) -> None:
        """
        Sets the article style guide.

        Args:
            style_guide (StyleGuide): The style guide to set.
        """
        logger.trace(f"Setting new style guide: {style_guide}")
        self.style_guide = style_guide

    def get_style_guide(self) -> StyleGuide:
        """
        Retrieves the current article style guide.

        Returns:
            StyleGuide: The current style guide of the article.
        """
        logger.trace("Retrieving current style guide.")
        return self.style_guide

    def style_guide_to_prompt(self) -> str:
        """
        Converts the style guide to a prompt string.

        Returns:
            str: The style guide represented as a prompt string.
        """
        sg = self.style_guide
        prompt_parts = [
            f"Main Language: {sg.main_language}",
            f"Tone: {sg.tone}",
            f"Voice: {sg.voice}",
            f"Target Audience: {sg.target_audience}",
        ]
        if sg.formatting_preferences:
            prompt_parts.append(f"Formatting Preferences: {sg.formatting_preferences}")
        return "\n".join(prompt_parts)

    @classmethod
    def get_tools(cls, attr_name: str | None = None) -> list[Tool]:
        """
        Returns the tools associated with the StyleManager.

        Returns:
            list[Tool]: A list of tools for interacting with the StyleManager.
        """

        def set_style_guide_tool(ctx: RunContext[Any], style_guide: StyleGuide) -> None:
            sm: StyleManager = getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            if sm is None or not isinstance(sm, cls):
                raise ValueError("StyleManager dependency is not provided.")
            sm.set_style_guide(style_guide)

        def get_style_guide_tool(ctx: RunContext[Any]) -> StyleGuide:
            sm: StyleManager = getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            if sm is None or not isinstance(sm, cls):
                raise ValueError("StyleManager dependency is not provided.")
            return sm.get_style_guide()

        return [
            Tool(
                set_style_guide_tool,
                takes_ctx=True,
                name="set_style_guide",
                description="Sets the article style guide.",
            ),
            Tool(
                get_style_guide_tool,
                takes_ctx=True,
                name="get_style_guide",
                description="Retrieves the current article style guide.",
            ),
        ]
