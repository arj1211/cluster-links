import os
import sys
from pathlib import Path

# Get the root directory (cluster-links)
ROOT_DIR = Path(__file__).resolve().parent.parent

# Get the src directory path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"


def setup():
    """Set up the notebook environment."""
    sys.path.append(str(ROOT_DIR))
    print(f"Added {ROOT_DIR} to Python path.")

    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))
        print(f"Added {SRC_DIR} to Python path")

    print(f"Current working directory: {Path.cwd()}")


if __name__ == "__main__":
    setup()
