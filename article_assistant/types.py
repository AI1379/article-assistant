#
# Created by Renatus Madrigal on 12/26/2025
#

from pydantic import BaseModel, Field
import re


class OutlineItem(BaseModel):
    """
    Represents a single item in the article outline.
    """

    title: str = Field(..., description="The title of the outline item.")
    purpose: str = Field(
        ...,
        description="The purpose of this outline item in the context of the article.",
    )
    argument: str = Field(
        ...,
        description="The argument or main point associated with this outline item.",
    )
    expected_conclusion: str = Field(
        ...,
        description="The expected conclusion or takeaway from this outline item.",
    )
    expected_length: int = Field(
        ...,
        description="The expected length (in words) of this outline item.",
    )


class Outline(BaseModel):
    """
    Represents the overall article outline.
    """

    outline_items: list[OutlineItem] = Field(
        ..., description="A list of outline items for the article."
    )


class StyleGuide(BaseModel):
    """
    Represents the style guide for articles.
    """

    main_language: str = Field(
        default="English",
        description="The main language of the article (e.g., English, Simplified Chinese).",
    )
    tone: str = Field(
        default="formal",
        description="The tone of the article (e.g., formal, informal).",
    )
    voice: str = Field(
        default="active",
        description="The voice of the article (e.g., active, passive).",
    )
    target_audience: str = Field(
        default="general",
        description="The target audience for the article.",
    )
    formatting_preferences: str = Field(
        default="",
        description="Any specific formatting preferences for the article.",
    )


class SectionInfo(BaseModel):
    """
    Represents information about a specific section of an article.
    """

    section_index: int = Field(
        ..., description="The index of the section in the article."
    )
    heading: str = Field(..., description="The heading of the section.")
    contents: str = Field(
        ...,
        description="The main contents of the section.",
    )
    summary: str = Field(
        ...,
        description="A brief summary of the section.",
    )

    @property
    def word_count(self) -> int:
        """
        Calculates the word count of the section contents.
        """
        # Split on whitespace for regular words
        words = self.contents.split()
        # Count Chinese characters (CJK Unified Ideographs) as individual words
        chinese_chars = re.findall(r"[\u4e00-\u9fff]", self.contents)
        return len(words) + len(chinese_chars)


class ConceptInfo(BaseModel):
    """
    Represents information about a specific concept related to the article.
    """

    name: str = Field(..., description="The name of the concept.")
    definition: str = Field(..., description="The definition of the concept.")
    relevance: str = Field(
        ...,
        description="The relevance of the concept to the article topic.",
    )
