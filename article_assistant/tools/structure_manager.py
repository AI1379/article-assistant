#
# Created by Renatus Madrigal on 12/26/2025
#

from typing import Any

from loguru import logger
from pydantic import BaseModel, Field, PrivateAttr
from pydantic_ai import RunContext, Tool

from article_assistant.types import Outline, OutlineItem, SectionInfo


class StructureManager(BaseModel):
    """
    Manages the structure of articles within the Article Assistant application.
    """

    outline: Outline = Field(
        default=Outline(outline_items=[]),
        description="The outline of the article, represented as a list of OutlineItem objects.",
    )
    sections: list[SectionInfo] = Field(
        default_factory=list,
        description="The sections of the article, represented as a list of SectionInfo objects.",
    )
    keywords: list[str] = Field(
        default=[], description="A list of keywords relevant to the article."
    )
    title: str = Field(default="", description="The title of the article.")

    _existed_section_idxs: set[int] = PrivateAttr(default_factory=set)

    def set_outline(self, outline: Outline) -> None:
        """
        Sets the article outline.

        Args:
            outline (Outline): The outline to set.
        """
        self.outline = outline

    def list_outline_items(self) -> list[OutlineItem]:
        """
        Lists all outline items in the article outline.

        Returns:
            list[OutlineItem]: A list of outline items.
        """
        return self.outline.outline_items

    def get_section_plan(self, section_index: int) -> OutlineItem:
        """
        Retrieves the plan for a specific section based on its index.

        Args:
            section_index (int): The index of the section to retrieve.
        Returns:
            OutlineItem: The plan for the specified section.
        """
        logger.info(f"Retrieving plan for section index: {section_index}")
        return self.outline.outline_items[section_index]

    def get_context_summary(self, section_index: int) -> str:
        """
        Generates a summary of the context for a specific section.

        Args:
            section_index (int): The index of the section to summarize.
        Returns:
            str: A summary of the section's context.
        """
        summary = "Previous Sections Summary:\n"
        for sec in self.sections[:section_index]:
            summary += f"- {sec.heading}: {sec.contents[:100]}...\n"

        logger.trace(f"Context summary for section index {section_index}: {summary}")
        return summary

    def add_section(self, section: SectionInfo) -> None:
        """
        Adds a new section to the article structure.

        Args:
            section (SectionInfo): The section to add.
        """
        logger.trace(f"Adding new section: {section}")
        if section.section_index in self._existed_section_idxs:
            logger.warning(
                f"Section with index {section.section_index} already exists. Skipping addition."
            )
            return
        self.sections.append(section)
        self._existed_section_idxs.add(section.section_index)

    def modify_section(self, section_index: int, new_content: str) -> None:
        """
        Modifies the content of an existing section.

        Args:
            section_index (int): The index of the section to modify.
            new_content (str): The new content for the section.
        """
        logger.trace(f"Modifying section index {section_index} with new content.")
        for section in self.sections:
            if section.section_index == section_index:
                section.contents = new_content
                return
        raise ValueError(f"Section with index {section_index} not found.")

    def get_section(self, section_index: int) -> SectionInfo:
        """
        Retrieves a section by its index.

        Args:
            section_index (int): The index of the section to retrieve.
        Returns:
            SectionInfo: The section with the specified index.
        """
        logger.info(f"Retrieving section with index: {section_index}")
        for section in self.sections:
            if section.section_index == section_index:
                return section
        raise ValueError(f"Section with index {section_index} not found.")

    def total_word_count(self) -> int:
        """
        Calculates the total word count of all sections in the article.

        Returns:
            int: The total word count.
        """
        total_count = 0
        for section in self.sections:
            total_count += section.word_count
        return total_count

    def to_markdown(self) -> str:
        """
        Converts the article structure to a markdown representation.
        Returns:
            str: The markdown representation of the article structure.
        """
        self.sections.sort(key=lambda s: s.section_index)
        md_content = ""
        md_content += f"# {self.title}\n\n"
        md_content += f"Keywords: {', '.join(self.keywords)}\n\n"
        md_content += "\n\n".join(
            f"## {section.heading}\n\n{section.contents}" for section in self.sections
        )
        return md_content

    def set_keywords(self, keywords: list[str]) -> None:
        """
        Sets the keywords for the article.

        Args:
            keywords (list[str]): The list of keywords to set.
        """
        logger.info(f"Setting keywords: {keywords}")
        self.keywords = keywords

    def get_keywords(self) -> list[str]:
        """
        Retrieves the keywords of the article.

        Returns:
            list[str]: The list of keywords.
        """
        logger.info("Retrieving article keywords.")
        return self.keywords

    def set_title(self, title: str) -> None:
        """
        Sets the title of the article.

        Args:
            title (str): The title to set.
        """
        logger.info(f"Setting title: {title}")
        self.title = title

    def get_title(self) -> str:
        """
        Retrieves the title of the article.

        Returns:
            str: The title of the article.
        """
        logger.info("Retrieving article title.")
        return self.title

    @classmethod
    def get_tools_prompt(cls) -> str:
        """
        Returns a prompt string describing the tools associated with the StructureManager.

        Returns:
            str: A prompt string for the StructureManager tools.
        """
        return (
            "You are supposed to use the StructureManager tools to make sure the sections "
            "of the article are well organized and follow the outline. "
        )

    @classmethod
    def get_tools(cls, attr_name: str | None = None) -> list[Tool]:
        """
        Returns the tools associated with the StructureManager.

        Returns:
            list[Tool]: A list of tools for interacting with the StructureManager.
        """

        def set_outline_tool(ctx: RunContext[Any], outline: Outline) -> None:
            sm: StructureManager = (
                getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            )
            if sm is None or not isinstance(sm, cls):
                raise ValueError("StructureManager dependency is not provided.")
            sm.set_outline(outline)

        def list_outline_items_tool(ctx: RunContext[Any]) -> list[OutlineItem]:
            sm: StructureManager = (
                getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            )
            if sm is None or not isinstance(sm, cls):
                raise ValueError("StructureManager dependency is not provided.")
            return sm.list_outline_items()

        def get_section_plan_tool(
            ctx: RunContext[Any], section_index: int
        ) -> OutlineItem:
            sm: StructureManager = (
                getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            )
            if sm is None or not isinstance(sm, cls):
                raise ValueError("StructureManager dependency is not provided.")
            return sm.get_section_plan(section_index)

        def get_context_summary_tool(ctx: RunContext[Any], section_index: int) -> str:
            sm: StructureManager = (
                getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            )
            if sm is None or not isinstance(sm, cls):
                raise ValueError("StructureManager dependency is not provided.")
            return sm.get_context_summary(section_index)

        def add_section_tool(ctx: RunContext[Any], section: SectionInfo) -> None:
            sm: StructureManager = (
                getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            )
            if sm is None or not isinstance(sm, cls):
                raise ValueError("StructureManager dependency is not provided.")
            sm.add_section(section)

        def modify_section_tool(
            ctx: RunContext[Any], section_index: int, new_content: str
        ) -> None:
            sm: StructureManager = (
                getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            )
            if sm is None or not isinstance(sm, cls):
                raise ValueError("StructureManager dependency is not provided.")
            sm.modify_section(section_index, new_content)

        def get_section_tool(ctx: RunContext[Any], section_index: int) -> SectionInfo:
            sm: StructureManager = (
                getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            )
            if sm is None or not isinstance(sm, cls):
                raise ValueError("StructureManager dependency is not provided.")
            return sm.get_section(section_index)

        def set_title_tool(ctx: RunContext[Any], title: str) -> None:
            sm: StructureManager = (
                getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            )
            if sm is None or not isinstance(sm, cls):
                raise ValueError("StructureManager dependency is not provided.")
            sm.set_title(title)

        def get_title_tool(ctx: RunContext[Any]) -> str:
            sm: StructureManager = (
                getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            )
            if sm is None or not isinstance(sm, cls):
                raise ValueError("StructureManager dependency is not provided.")
            return sm.get_title()

        def set_keywords_tool(ctx: RunContext[Any], keywords: list[str]) -> None:
            sm: StructureManager = (
                getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            )
            if sm is None or not isinstance(sm, cls):
                raise ValueError("StructureManager dependency is not provided.")
            sm.set_keywords(keywords)

        def get_keywords_tool(ctx: RunContext[Any]) -> list[str]:
            sm: StructureManager = (
                getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            )
            if sm is None or not isinstance(sm, cls):
                raise ValueError("StructureManager dependency is not provided.")
            return sm.get_keywords()

        return [
            Tool(
                set_outline_tool,
                takes_ctx=True,
                name="StructureManager_set_outline",
                description="Sets the article outline.",
            ),
            Tool(
                list_outline_items_tool,
                takes_ctx=True,
                name="StructureManager_list_outline_items",
                description="Lists all outline items in the article outline.",
            ),
            Tool(
                get_section_plan_tool,
                takes_ctx=True,
                name="StructureManager_get_section_plan",
                description="Retrieves the plan for a specific section based on its index.",
            ),
            Tool(
                get_context_summary_tool,
                takes_ctx=True,
                name="StructureManager_get_context_summary",
                description="Generates a summary of the context for a specific section.",
            ),
            Tool(
                add_section_tool,
                takes_ctx=True,
                name="StructureManager_add_section",
                description="Adds a new section to the article structure.",
            ),
            Tool(
                modify_section_tool,
                takes_ctx=True,
                name="StructureManager_modify_section",
                description="Modifies the content of an existing section.",
            ),
            Tool(
                get_section_tool,
                takes_ctx=True,
                name="StructureManager_get_section",
                description="Retrieves a section by its index.",
            ),
            Tool(
                set_title_tool,
                takes_ctx=True,
                name="StructureManager_set_title",
                description="Sets the title of the article.",
            ),
            Tool(
                get_title_tool,
                takes_ctx=True,
                name="StructureManager_get_title",
                description="Retrieves the title of the article.",
            ),
            Tool(
                set_keywords_tool,
                takes_ctx=True,
                name="StructureManager_set_keywords",
                description="Sets the keywords of the article.",
            ),
            Tool(
                get_keywords_tool,
                takes_ctx=True,
                name="StructureManager_get_keywords",
                description="Retrieves the keywords of the article.",
            ),
        ]
