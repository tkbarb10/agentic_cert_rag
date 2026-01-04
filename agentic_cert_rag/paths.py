from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

PROMPT_CONFIG_FPATH = ROOT_DIR / "config" / "prompts.yaml"
OUTPUTS_DIR = ROOT_DIR / "data" / "outputs"
