#
# Created by Renatus Madrigal on 12/26/2025
#

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    model_name: str = Field(
        ...,
        description="The name of the language model to use.",
    )
    api_key: str = Field(
        ...,
        description="The API key for accessing the language model service.",
    )
    base_url: str = Field(
        "",
        description="The base URL for the language model service API.",
    )


class Config(BaseModel):
    llm: LLMConfig = Field(
        ...,
        description="Configuration settings for the language model.",
    )
