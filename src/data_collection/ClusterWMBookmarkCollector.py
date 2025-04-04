from .BookmarkCollector import BookmarkCollector


class ClusterWMBookmarkCollector(BookmarkCollector):
    """Collector for Cluster Window Manager (Chrome Extension) export."""

    def process_bookmarks(self):
        self.file_type = "csv" if self.file_path.endswith(".csv") else None
        self.file_type = "json" if self.file_path.endswith(".json") else None

        if not self.file_type:
            raise ValueError(f"{self.file_path} must be of type [`csv`, `json`]")

        self.bookmarks = ...
