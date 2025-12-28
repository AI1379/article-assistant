#
# Created by Renatus Madrigal on 12/26/2025
#

from typing import Any

from loguru import logger
from pydantic import BaseModel, Field
from pydantic_ai import RunContext, Tool

from article_assistant.types import ConceptInfo


class KnowledgeBase(BaseModel):
    concepts: list[ConceptInfo] = Field(
        default=[],
        description="A list of concepts stored in the knowledge base.",
    )

    def add_concept(self, concept: ConceptInfo) -> None:
        """
        Adds a new concept to the knowledge base.

        Args:
            concept (ConceptInfo): The concept to add.
        """
        logger.info(f"Adding new concept: {concept}")
        self.concepts.append(concept)

    def get_concept(self, name: str) -> ConceptInfo | None:
        """
        Retrieves a concept by name.

        Args:
            name (str): The name of the concept to retrieve.
        Returns:
            ConceptInfo | None: The concept if found, else None.
        """
        logger.info(f"Retrieving concept by name: {name}")
        for concept in self.concepts:
            if concept.name == name:
                return concept
        return None

    def list_concepts(self) -> list[str]:
        """
        Lists all concept names in the knowledge base.

        Returns:
            list[str]: A list of concept names.
        """
        logger.info("Listing all concept names in the knowledge base.")
        return [concept.name for concept in self.concepts]

    @classmethod
    def get_tools_prompt(cls) -> str:
        """
        Returns a prompt string describing the tools associated with the KnowledgeBase.

        Returns:
            str: A prompt string for the KnowledgeBase tools.
        """
        return (
            "You have access to the following KnowledgeBase tools:\n"
            "1. KnowledgeBase_get_concept: Retrieve a concept by name from the knowledge base.\n"
            "2. KnowledgeBase_add_concept: Add a new concept to the knowledge base.\n"
            "3. KnowledgeBase_list_concepts: List all concept names in the knowledge base.\n"
        )

    @classmethod
    def get_tools(cls, attr_name: str | None = None) -> list[Tool]:
        """
        Returns the tools associated with the KnowledgeBase.

        Returns:
            list[Tool]: A list of tools for interacting with the KnowledgeBase.
        """

        def add_concept_tool(ctx: RunContext[Any], concept: ConceptInfo) -> None:
            kb: KnowledgeBase = getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            if kb is None or not isinstance(kb, cls):
                raise ValueError("KnowledgeBase dependency is not provided.")
            kb.add_concept(concept)

        def get_concept_tool(ctx: RunContext[Any], name: str) -> ConceptInfo | None:
            kb: KnowledgeBase = getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            if kb is None or not isinstance(kb, cls):
                raise ValueError("KnowledgeBase dependency is not provided.")
            return kb.get_concept(name)

        def list_concepts_tool(ctx: RunContext[Any]) -> list[str]:
            kb: KnowledgeBase = getattr(ctx.deps, attr_name) if attr_name else ctx.deps
            if kb is None or not isinstance(kb, cls):
                raise ValueError("KnowledgeBase dependency is not provided.")
            return kb.list_concepts()

        return [
            Tool(
                get_concept_tool,
                takes_ctx=True,
                name="KnowledgeBase_get_concept",
                description="Retrieve a concept by name from the knowledge base.",
            ),
            Tool(
                add_concept_tool,
                takes_ctx=True,
                name="KnowledgeBase_add_concept",
                description="Add a new concept to the knowledge base.",
            ),
            Tool(
                list_concepts_tool,
                takes_ctx=True,
                name="KnowledgeBase_list_concepts",
                description="List all concept names in the knowledge base.",
            ),
        ]
