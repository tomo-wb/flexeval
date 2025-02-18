from __future__ import annotations

from flexeval.core.multiple_choice_dataset import MultipleChoiceDataset, MultipleChoiceInstance


class DummyMultipleChoiceDataset(MultipleChoiceDataset):
    def __init__(self) -> None:
        self._data = [
            MultipleChoiceInstance(
                inputs={"text": "This is"},
                choices=["a test", "not a test"],
                answer_index=0,
            ),
            MultipleChoiceInstance(
                inputs={"text": "That is"},
                choices=["a test", "not a test"],
                answer_index=0,
            ),
        ]

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, item: int) -> MultipleChoiceInstance:
        return self._data[item]
