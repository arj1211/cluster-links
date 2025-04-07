import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union


class BookmarkLoader(ABC):
    def __init__(self, file_path: Union[str, Path], **kwargs):
        """Initialize path to bookmarks file and process bookmarks"""
        self.file_path = Path(file_path) if isinstance(file_path, str) else file_path
        self.bookmarks = None
        self.process_bookmarks(**kwargs)

    @abstractmethod
    def process_bookmarks(self, **kwargs) -> None:
        """Process the bookmarks file and populate self.bookmarks."""
        pass

    def get_bookmarks(self) -> Dict[str, Any]:
        """Return the processed bookmarks."""
        if self.bookmarks is None:
            raise ValueError("Bookmarks have not been processed yet.")
        return self.bookmarks

    def as_json(self) -> str:
        """Return the bookmarks as a JSON string."""
        if self.bookmarks is None:
            raise ValueError("Bookmarks have not been processed yet.")
        return json.dumps(self.bookmarks, indent=2)

    def save_json(
        self, output_path: Union[str, Path], return_path=False
    ) -> Optional[Path]:
        """Save the bookmarks to a JSON file."""
        output_path = Path(output_path) if isinstance(output_path, str) else output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.as_json())

        if return_path:
            return output_path
