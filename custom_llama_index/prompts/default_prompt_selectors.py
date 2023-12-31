"""Prompt selectors."""
from langchain.chains.prompt_selector import ConditionalPromptSelector, is_chat_model

from custom_llama_index.prompts.chat_prompts import (
    CHAT_REFINE_PROMPT,
    CHAT_REFINE_TABLE_CONTEXT_PROMPT,
)
from custom_llama_index.prompts.default_prompts import (
    DEFAULT_REFINE_PROMPT,
    DEFAULT_REFINE_TABLE_CONTEXT_PROMPT,
)
from custom_llama_index.prompts.prompts import RefinePrompt, RefineTableContextPrompt

DEFAULT_REFINE_PROMPT_SEL_LC = ConditionalPromptSelector(
    default_prompt=DEFAULT_REFINE_PROMPT.get_langchain_prompt(),
    conditionals=[(is_chat_model, CHAT_REFINE_PROMPT.get_langchain_prompt())],
)
DEFAULT_REFINE_PROMPT_SEL = RefinePrompt(
    langchain_prompt_selector=DEFAULT_REFINE_PROMPT_SEL_LC
)

DEFAULT_REFINE_TABLE_CONTEXT_PROMPT_SEL_LC = ConditionalPromptSelector(
    default_prompt=DEFAULT_REFINE_TABLE_CONTEXT_PROMPT.get_langchain_prompt(),
    conditionals=[
        (is_chat_model, CHAT_REFINE_TABLE_CONTEXT_PROMPT.get_langchain_prompt())
    ],
)

DEFAULT_REFINE_TABLE_CONTEXT_PROMPT_SEL = RefineTableContextPrompt(
    langchain_prompt_selector=DEFAULT_REFINE_TABLE_CONTEXT_PROMPT_SEL_LC
)
