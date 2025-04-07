from .BookmarkLoader import BookmarkLoader


class ClusterWMBookmarkLoader(BookmarkLoader):
    """Loader for Cluster Window Manager (Chrome Extension) export."""

    _column_mappings = {
        "window": "folder",
        "url": "href",
        "title": "title",
        "hostname": "hostname",
    }

    def process_bookmarks(self, **kwargs):

        self.file_type = None
        if self.file_path.suffix == ".csv":
            self.file_type = "csv"
        elif self.file_path.suffix == ".json":
            self.file_type = "json"

        if not self.file_type:
            raise ValueError(f"{self.file_path} must be of type [`csv`, `json`]")

        assert self.file_type == "csv", "ERR - json not implemented yet, use csv"
        self.bookmarks = self._load_from_csv()

    def _load_from_csv(self):
        import pandas as pd

        df = (
            pd.read_csv(self.file_path).rename(columns=self._column_mappings).fillna("")
        )
        df["folder"] = df["folder"].str.extract(r"([a-zA-Z\-]+[a-zA-Z])")
        df = (
            df.drop_duplicates()
            .loc[df["href"].str.strip() != "chrome://newtab/"]
            .groupby("href")
            .apply(self._dedup_href, include_groups=False)
            .reset_index()
        )

        bm_folder_list = list(
            map(
                lambda x: {
                    "title": x,
                    "links": df.loc[df["folder"] == x][
                        [c for c in self._column_mappings.values() if c != "folder"]
                    ].to_dict(orient="records"),
                },
                df["folder"].unique().tolist(),
            )
        )
        bm_root = {"title": "Unnamed", "children": bm_folder_list}

        return bm_root

    def _load_from_json(self): ...

    def _dedup_href(self, group):
        if len(group) == 1:
            return group

        group_columns = group.columns
        max_record = group[group_columns[0]].str.len()
        for i in range(1, len(group_columns)):
            max_record += group[group_columns[i]].str.len()
        max_idx = max_record.idxmax()

        return group.loc[[max_idx]]
