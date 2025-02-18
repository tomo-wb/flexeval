from __future__ import annotations

import pytest

from flexeval.core.chat_dataset import ChatbotBench, ChatInstance


@pytest.mark.parametrize(
    ("dataset_name", "ref_name"),
    [
        ("mt-en", "mt-en-ref-gpt4"),
        ("mt-ja", "mt-ja-ref-gpt4"),
        ("rakuda-v2-ja", None),
        ("vicuna-en", "vicuna-en-ref-gpt4"),
        ("vicuna-ja", "vicuna-ja-ref-gpt4"),
    ],
)
def test_chatbot_bench(dataset_name: str, ref_name: str | None) -> None:
    dataset = ChatbotBench(
        file_path_or_name=dataset_name,
        ref_file_path_or_name=ref_name,
        need_ref_categories=None,
    )

    assert len(dataset) > 0
    assert isinstance(dataset[0], ChatInstance)

    if ref_name is None:
        assert all(len(instance.references) == 0 for instance in dataset)
    else:
        assert any(len(instance.references) > 0 for instance in dataset)
