from __future__ import annotations

import json
import os
import subprocess
import tempfile
from os import PathLike
from pathlib import Path
from typing import Any

import pytest

from flexeval.scripts.flexeval_pairwise import (
    CONFIG_FILE_NAME,
)

from .test_flexeval_lm import check_if_eval_results_are_correctly_saved


def read_jsonl(path: str | PathLike[str]) -> list[dict[str, Any]]:
    with open(path) as f:
        return [json.loads(line) for line in f]


@pytest.mark.parametrize(
    "judge_args",
    [
        ["--judge", "tests.dummy_modules.DummyPairwiseJudge"],
        ["--judge", "pairwise_judge"],
    ],
)
def test_flexeval_pairwise_cli(judge_args: list[str]) -> None:
    os.environ["PRESET_CONFIG_JUDGE_DIR"] = str(Path(__file__).parent.parent / "dummy_modules" / "configs")

    with tempfile.TemporaryDirectory() as f:
        dummy_model_data_path = str(Path(f) / "dummy_model_data.jsonl")
        with open(dummy_model_data_path, "w") as file:
            file.write(json.dumps({"lm_output": "dummy"}) + "\n")

        # fmt: off
        command = [
            "flexeval_pairwise",
            "--lm_output_paths", json.dumps({"model1": dummy_model_data_path, "model2": dummy_model_data_path}),
            *judge_args,
            "--save_dir", f,
        ]
        # fmt: on

        result = subprocess.run(command, check=False)
        assert result.returncode == os.EX_OK

        check_if_eval_results_are_correctly_saved(f)


def test_if_flexeval_pairwise_cli_raises_error_when_save_data_exists() -> None:
    with tempfile.TemporaryDirectory() as f:
        (Path(f) / CONFIG_FILE_NAME).touch()

        dummy_model_data_path = str(Path(f) / "dummy_model_data.jsonl")
        with open(dummy_model_data_path, "w") as file:
            file.write(json.dumps({"lm_output": "dummy"}) + "\n")

        # fmt: off
        command = [
            "flexeval_pairwise",
            "--lm_output_paths", json.dumps({"model1": dummy_model_data_path, "model2": dummy_model_data_path}),
            "--judge", "tests.dummy_modules.DummyPairwiseJudge",
            "--save_dir", f,
        ]
        # fmt: on
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.check_output(command)


def test_if_saved_config_can_be_reused_to_run_eval() -> None:
    with tempfile.TemporaryDirectory() as f:
        dummy_model_data_path = str(Path(f) / "dummy_model_data.jsonl")
        with open(dummy_model_data_path, "w") as file:
            file.write(json.dumps({"lm_output": "dummy"}) + "\n")

        # fmt: off
        command = [
            "flexeval_pairwise",
            "--lm_output_paths", json.dumps({"model1": dummy_model_data_path, "model2": dummy_model_data_path}),
            "--judge", "tests.dummy_modules.DummyPairwiseJudge",
            "--save_dir", f,
        ]
        # fmt: on

        result = subprocess.run(command, check=False)
        assert result.returncode == os.EX_OK

        saved_config_file_path = str(Path(f) / CONFIG_FILE_NAME)
        with open(saved_config_file_path) as f_json:
            assert json.load(f_json)

        new_save_path = str(Path(f) / "new_save_dir")
        # fmt: off
        command = [
            "flexeval_pairwise",
            "--config", saved_config_file_path,
            "--save_dir", new_save_path,
        ]
        # fmt: on
        result = subprocess.run(command, check=False)
        assert result.returncode == os.EX_OK

        new_saved_config_file_path = str(Path(new_save_path) / CONFIG_FILE_NAME)

        # check if the contents of the saved config are the same
        with open(saved_config_file_path) as f_json:
            saved_config = json.load(f_json)
        with open(new_saved_config_file_path) as f_json:
            new_saved_config = json.load(f_json)
        for key in saved_config:
            if key in {"save_dir", "config"}:
                continue
            assert saved_config[key] == new_saved_config[key]
