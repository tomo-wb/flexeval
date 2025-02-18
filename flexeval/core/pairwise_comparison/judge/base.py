from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class Winner(Enum):
    """
    Enum class to indicate the winner of a pairwise comparison.
    """

    MODEL1 = "model1"
    MODEL2 = "model2"
    DRAW = "draw"

    def __str__(self) -> str:
        # used when serializing to JSON
        return self.value


class PairwiseJudge(ABC):
    """Judge which model is better given two items.

    The output is a tuple of the winner and the rationale.
    """

    @abstractmethod
    def judge(
        self,
        model1_item: dict[str, Any],
        model2_item: dict[str, Any],
    ) -> tuple[Winner, str]:
        """
        Judge which model is better given two items.

        Args:
            model1_item: The first model item, containing the model output and other information needed for judging.
            model2_item: The second model item, containing the model output and other information needed for judging.

        Returns:
            A tuple of the winner and the rationale.
        """

    @abstractmethod
    def batch_judge(
        self,
        batch_model_items: list[tuple[dict[str, Any], dict[str, Any]]],
    ) -> list[tuple[Winner, str]]:
        """
        Judge which model is better given a batch of item pairs.

        Args:
            batch_model_items: A list of tuples, each containing two model items.
        """
