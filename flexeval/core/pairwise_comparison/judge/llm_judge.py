from __future__ import annotations

import logging
import re
from typing import Any

from flexeval.core.language_model.base import LanguageModel
from flexeval.core.prompt_template.base import PromptTemplate

from .base import PairwiseJudge, Winner

logger = logging.getLogger(__name__)


class ChatLLMPairwiseJudge(PairwiseJudge):
    """
    Pairwise judge using a chat language model to compare two model outputs.

    Args:
        language_model: The language model to use for pairwise comparison.
        prompt_template: The prompt template to embed the model outputs to be compared.
        system_message: The system message to prepend to the chat messages.
    """

    def __init__(
        self,
        language_model: LanguageModel,
        prompt_template: PromptTemplate,
        system_message: str | None = None,
    ) -> None:
        self._language_model = language_model
        self._prompt_template = prompt_template
        self._system_message = system_message

    @staticmethod
    def _parse_judge_output(judge_output: str) -> tuple[Winner, str]:
        """Extract the last integer value from the judge output and return the
        corresponding Winner and its rationale.

        Return `Winner.DRAW` if parsing fails.
        """
        try:
            matched = re.findall(r"(\d+)", judge_output)
            value = int(matched[-1])
            winner: Winner
            rationale = judge_output
            if value == 1:
                winner = Winner.MODEL1
            elif value == 2:
                winner = Winner.MODEL2
            elif value == 3:
                winner = Winner.DRAW
            else:
                logger.warning(f"Invalid number {value} was extracted:\n\n{judge_output}")
                winner = Winner.DRAW
                rationale = f"Invalid judge '{value}': {judge_output}"
        except (IndexError, ValueError):
            logger.warning(f"Failed to extract the judgment result:\n\n{judge_output}")
            return Winner.DRAW, f"Parsing failure: {judge_output}"
        else:
            return winner, rationale

    def judge(self, model1_item: dict[str, Any], model2_item: dict[str, Any]) -> tuple[Winner, str]:
        return self.batch_judge([(model1_item, model2_item)])[0]

    def batch_judge(self, batch_model_items: list[tuple[dict[str, Any], dict[str, Any]]]) -> list[tuple[Winner, str]]:
        input_chat_messages_list: list[list[dict[str, str]]] = []
        for model1_item, model2_item in batch_model_items:
            references = model1_item["references"]
            prompt_inputs = {
                "model1_item": model1_item,
                "model2_item": model2_item,
                "references": references,
            }
            self._prompt_template.embed_input(prompt_inputs)
            judge_input = self._prompt_template.embed_input(prompt_inputs)
            input_chat_messages = [{"role": "user", "content": judge_input}]
            if self._system_message:
                input_chat_messages.insert(0, {"role": "system", "content": self._system_message})
            input_chat_messages_list.append(input_chat_messages)
        judge_outputs = self._language_model.batch_generate_chat_response(input_chat_messages_list)
        return [self._parse_judge_output(output) for output in judge_outputs]
