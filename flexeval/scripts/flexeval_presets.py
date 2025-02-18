from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Show predefined configurations.")

    # add optional argument for the preset name
    parser.add_argument("preset", type=str, nargs="?", help="Name of the preset")

    args = parser.parse_args()

    all_configs: dict[str, list[str]] = {}
    all_config_paths: dict[str, Path] = {}
    for config_class, dir_env_key in [
        ("EvalSetup", "PRESET_CONFIG_EVAL_DIR"),
        ("Metric", "PRESET_CONFIG_METRIC_DIR"),
        ("PairwiseJudge", "PRESET_CONFIG_JUDGE_DIR"),
    ]:
        config_directory = os.environ.get(
            dir_env_key,
            Path(__file__).parent.parent / "preset_configs" / config_class,
        )

        config_paths = {config_path.stem: config_path for config_path in Path(config_directory).rglob("*.jsonnet")}

        all_configs[config_class] = sorted(config_paths.keys())
        all_config_paths.update(config_paths)

    if args.preset:
        if args.preset not in all_config_paths:
            sys.stdout.write(f"Preset {args.preset} not found.\n")
            sys.stdout.write("Please choose from a list shown by `flexeval_presets`.\n")
            sys.exit(os.EX_DATAERR)
        else:
            with open(all_config_paths[args.preset]) as f:
                sys.stdout.write(f.read())
                sys.stdout.flush()
            sys.exit(os.EX_OK)

    for config_class, available_configs in all_configs.items():
        sys.stdout.write(f"{config_class}\n")
        sys.stdout.write("\t" + json.dumps(available_configs))

        if config_class == "EvalSetup":
            msg = "Can be specified as `flexeval_lm --eval_setup <preset_name>`."
        elif config_class == "Metric":
            msg = "Can be specified as `flexeval_file --metrics <preset_name>`."
        elif config_class == "PairwiseJudge":
            msg = "Can be specified as `flexeval_pairwise --judge <preset_name>`."
        else:
            error_msg = f"Unknown config class: {config_class}"
            raise ValueError(error_msg)

        sys.stdout.write(f"\n\t{msg}\n")
        sys.stdout.write("\n")
        sys.stdout.flush()

    sys.stdout.write("Use `flexeval_presets <preset_name>` to see the configuration.\n")
    sys.exit(os.EX_OK)


if __name__ == "__main__":
    main()
