import json
from pathlib import Path


def load_config(file_path=Path(__file__).parent.joinpath("config.json")):
    path = Path(file_path).expanduser()
    with path.open("r", encoding="utf-8") as f:
        config = json.load(f)
    return config
