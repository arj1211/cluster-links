import base64
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class BookmarkLink(BaseModel):
    """Represents a single bookmark link."""

    title: str
    href: str  # We're not using HttpUrl as some bookmarks might be local files or special URLs
    add_date: Optional[str] = None
    icon: Optional[str] = None

    # Additional attributes that might be present
    last_modified: Optional[str] = None
    tags: Optional[str] = None

    # A dictionary for any additional attributes
    extra_attributes: Dict[str, Any] = Field(default_factory=dict)

    @validator("href")
    def validate_href(cls, v):
        """Basic URL validation while allowing for flexibility."""
        if not v:
            raise ValueError("URL cannot be empty")
        return v

    @validator("add_date", "last_modified", pre=True)
    def validate_date(cls, v):
        """Convert Unix timestamp to ISO format if needed."""
        if not v:
            return None

        # Check if it's a Unix timestamp (numeric string)
        if isinstance(v, str) and v.isdigit():
            try:
                # Convert Unix timestamp to ISO format
                timestamp = int(v)
                return datetime.fromtimestamp(timestamp).isoformat()
            except (ValueError, OverflowError):
                return v
        return v

    @property
    def domain(self) -> str:
        """Extract domain from URL."""
        if not self.href:
            return ""

        match = re.search(r"https?://([^/]+)", self.href)
        if match:
            return match.group(1)
        return ""

    @property
    def decoded_icon(self) -> Optional[bytes]:
        """Decode base64 icon if present."""
        if not self.icon or not self.icon.startswith("data:image"):
            return None

        try:
            # Parse the data URL
            _, data = self.icon.split(",", 1)
            return base64.b64decode(data)
        except Exception:
            return None


class BookmarkFolder(BaseModel):
    """Represents a folder containing bookmarks and subfolders."""

    title: str
    add_date: Optional[str] = None
    last_modified: Optional[str] = None
    personal_toolbar_folder: Optional[str] = None

    # Links in this folder
    links: List[BookmarkLink] = Field(default_factory=list)

    # Child folders
    children: List["BookmarkFolder"] = Field(default_factory=list)

    # Any additional attributes
    extra_attributes: Dict[str, Any] = Field(default_factory=dict)

    @validator("add_date", "last_modified", pre=True)
    def validate_date(cls, v):
        """Convert Unix timestamp to ISO format if needed."""
        if not v:
            return None

        # Check if it's a Unix timestamp (numeric string)
        if isinstance(v, str) and v.isdigit():
            try:
                # Convert Unix timestamp to ISO format
                timestamp = int(v)
                return datetime.fromtimestamp(timestamp).isoformat()
            except (ValueError, OverflowError):
                return v
        return v

    @property
    def total_links_count(self) -> int:
        """Count total links in this folder and all subfolders."""
        count = len(self.links)
        for child in self.children:
            count += child.total_links_count
        return count

    @property
    def folders_tree(self) -> List[str]:
        """Get a list of all folder names in the tree."""
        result = [self.title]
        for child in self.children:
            for name in child.folders_tree:
                result.append(f"{self.title} > {name}")
        return result

    def find_links_by_domain(self, domain: str) -> List[BookmarkLink]:
        """Find all links with matching domain."""
        result = []

        # Check links in this folder
        for link in self.links:
            if domain in link.domain:
                result.append(link)

        # Check subfolders
        for child in self.children:
            result.extend(child.find_links_by_domain(domain))

        return result

    def find_folder_by_path(self, path: List[str]) -> Optional["BookmarkFolder"]:
        """Find a folder by path (list of folder names)."""
        if not path:
            return self

        current_name = path[0]
        remaining_path = path[1:]

        # Look for matching child folder
        for child in self.children:
            if child.title == current_name:
                if not remaining_path:
                    return child
                return child.find_folder_by_path(remaining_path)

        return None


class BookmarksRoot(BaseModel):
    """Root container for the entire bookmarks hierarchy."""

    title: str
    links: List[BookmarkLink] = Field(default_factory=list)
    children: List[BookmarkFolder] = Field(default_factory=list)

    @property
    def total_bookmarks(self) -> int:
        """Count all bookmarks in the hierarchy."""
        count = len(self.links)
        for folder in self.children:
            count += folder.total_links_count
        return count

    @property
    def total_folders(self) -> int:
        """Count all folders in the hierarchy."""
        count = len(self.children)
        for folder in self.children:
            count += (
                len(folder.folders_tree) - 1
            )  # -1 to avoid counting the folder itself twice
        return count

    def find_folder_by_path(self, path: List[str]) -> Optional[BookmarkFolder]:
        """Find a folder by path (list of folder names)."""
        if not path:
            return None

        # Look for the first folder in the path
        first_folder_name = path[0]
        remaining_path = path[1:]

        for folder in self.children:
            if folder.title == first_folder_name:
                if not remaining_path:
                    return folder
                return folder.find_folder_by_path(remaining_path)

        return None

    def find_links_by_domain(self, domain: str) -> List[BookmarkLink]:
        """Find all links with matching domain."""
        result = []

        # Check links in root
        for link in self.links:
            if domain in link.domain:
                result.append(link)

        # Check all folders
        for folder in self.children:
            result.extend(folder.find_links_by_domain(domain))

        return result

    def get_flat_bookmarks(self) -> List[Dict[str, Any]]:
        """Return all bookmarks as a flat list with path information."""
        result = []

        # Add root bookmarks
        for link in self.links:
            result.append(
                {
                    "title": link.title,
                    "url": link.href,
                    "folder": self.title,
                    "path": [self.title],
                    "add_date": link.add_date,
                    "domain": link.domain,
                }
            )

        # Add bookmarks from folders
        for folder in self.children:
            self._add_folder_bookmarks(folder, [self.title], result)

        return result

    def _add_folder_bookmarks(
        self, folder: BookmarkFolder, path: List[str], result: List[Dict[str, Any]]
    ):
        """Helper method to flatten bookmarks hierarchy."""
        current_path = path + [folder.title]

        # Add bookmarks from this folder
        for link in folder.links:
            result.append(
                {
                    "title": link.title,
                    "url": link.href,
                    "folder": folder.title,
                    "path": current_path.copy(),
                    "add_date": link.add_date,
                    "domain": link.domain,
                }
            )

        # Process subfolders
        for child in folder.children:
            self._add_folder_bookmarks(child, current_path, result)


# Add support for circular references in BookmarkFolder
BookmarkFolder.update_forward_refs()


# Helper functions for loading and validating bookmarks
def load_bookmarks_from_json(json_path):
    """Load and validate bookmarks from a JSON file."""
    import json
    from pathlib import Path

    path = Path(json_path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return BookmarksRoot(**data)


def load_bookmarks_from_dict(data):
    """Load and validate bookmarks from a dictionary."""
    return BookmarksRoot(**data)
