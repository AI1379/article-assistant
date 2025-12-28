#
# Created by Renatus Madrigal on 12/28/2025
#

from loguru import logger
from pydantic_ai.models import Model

from article_assistant.agents.architect import ArchitectDeps, create_architect_agent
from article_assistant.agents.scriber import ScriberDeps, create_scriber_agent
from article_assistant.agents.stylist import create_stylist_agent
from article_assistant.agents.reviewer import create_reviewer_agent, ReviewerDeps
from article_assistant.tools import (
    KnowledgeBase,
    StructureManager,
    StyleManager,
    get_base_tools,
)


async def generate_article_workflow(
    model: str | Model,
    topic: str,
    target_language: str,
    target_audience: str,
) -> str:
    logger.info("Starting article generation workflow.")
    kb = KnowledgeBase()
    structure_manager = StructureManager()

    architect_agent = create_architect_agent(
        model,
        additional_tools=get_base_tools(),
    )

    outline = await architect_agent.run(
        f"Create a detailed outline for an article about {topic}. 3 sections apart from introduction and conclusion in total.",
        deps=ArchitectDeps(structure_manager=structure_manager),
    )

    logger.info("Outline created by Architect Agent.")
    logger.debug(f"Outline Output: {outline.output}")

    structure_manager.set_outline(outline.output)

    section_count = len(structure_manager.outline.outline_items)
    logger.info(f"Outline contains {section_count} items.")

    stylist = create_stylist_agent(
        model,
        additional_tools=get_base_tools(),
        target_language=target_language,
    )

    style_result = await stylist.run(
        (
            f"Create a style guide for an article about {topic}. "
            f"The target audience is {target_audience}."
        ),
    )

    logger.info("Style guide created by Stylist Agent.")
    logger.debug(f"Style Guide Output: {style_result.output}")

    style_manager = StyleManager(style_guide=style_result.output)

    scriber_deps = ScriberDeps(
        style_manager=style_manager,
        knowledge_base=kb,
        structure_manager=structure_manager,
    )
    scriber_agent = create_scriber_agent(
        model,
        additional_tools=get_base_tools(),
    )

    for idx, outline_item in enumerate(structure_manager.outline.outline_items[1:-1]):
        prompt = (
            f"Write a detailed section for the outline item titled '{outline_item.title}'. "
            f"Use the purpose '{outline_item.purpose}' to guide the content. "
            f"Refer to the style guide and knowledge base as needed. "
            f"Ensure the content is in {target_language}."
        )
        section_result = await scriber_agent.run(
            prompt,
            deps=scriber_deps,
        )
        structure_manager.add_section(section_result.output)
        logger.info(f"Section {idx + 1}/{section_count} written by Scriber Agent.")

    # Generate introduction and conclusion sections
    for special_item_idx in [0, -1]:
        special_item = structure_manager.outline.outline_items[special_item_idx]
        prompt = (
            f"Write a detailed section for the outline item titled '{special_item.title}'. "
            f"Use the purpose '{special_item.purpose}' to guide the content. "
            f"Refer to the style guide and knowledge base as needed. "
            f"Ensure the content is in {target_language}."
        )
        section_result = await scriber_agent.run(
            prompt,
            deps=scriber_deps,
        )
        structure_manager.add_section(section_result.output)
        logger.info(f"Section '{special_item.title}' written by Scriber Agent.")

    logger.info("Reviewing the entire article with Reviewer Agent.")

    reviewer_deps = ReviewerDeps(
        structure_manager=structure_manager,
        style_manager=style_manager,
        knowledge_base=kb,
    )

    reviewer_agent = create_reviewer_agent(
        model,
        additional_tools=get_base_tools(),
    )

    review_result = await reviewer_agent.run(
        "Review the entire article for structure, style, and factual accuracy. "
        "Make necessary modifications and suggest a title and keywords for the article.",
        deps=reviewer_deps,
    )

    logger.info("Article reviewed by Reviewer Agent.")
    logger.debug(f"Review Output: {review_result.output}")

    print("\n--- Final Article Sections ---\n")

    for section in structure_manager.sections:
        print(f"Section Title: {section.heading}\nContent:\n{section.contents}\n")

    print("\n--- Knowledge Base Concepts ---\n")
    print(kb.list_concepts())
    return structure_manager.to_markdown()
