from .BookmarkLoader import BookmarkLoader


class ChromeBookmarkLoader(BookmarkLoader):
    """Loader for Chrome bookmarks export."""

    def process_bookmarks(self, pre_clean=True, **kwargs) -> None:
        """Process Chrome bookmarks HTML file."""
        if pre_clean:
            self.file_path, self._original_file_path = (
                self._clean_bookmarks_file(),
                self.file_path,
            )
        from bs4 import BeautifulSoup

        self.soup = BeautifulSoup(
            self.file_path.read_text(encoding="utf-8"), "html.parser"
        )
        self.root_element = self._get_root_dl()
        self.bookmarks = self._parse_dl(self.root_element)
        if pre_clean:
            import os

            os.remove(self.file_path)
            self.file_path = self._original_file_path

    def _get_root_dl(self):
        """Get the root DL element from the HTML."""
        dl_elements = self.soup.find_all("dl", recursive=False)
        if not dl_elements:
            raise ValueError("No root DL element found in the bookmarks file.")
        return dl_elements[0]

    def _parse_a_href(self, a_href_elem):
        """Parse an A tag (bookmark link)."""
        attrs = dict(a_href_elem.attrs)
        r_obj = {"title": " ".join(a_href_elem.text.replace("\n", "").split())}
        for k, v in attrs.items():
            r_obj[k] = v
        return r_obj

    def _parse_dl_elem(self, dl_elem):
        """Parse a DL element (folder)."""
        h3_elem = dl_elem.find_previous("h3", recursive=False)
        h3_obj = (
            {"title": "Unnamed"}
            if not h3_elem
            else {"title": h3_elem.text, **{k: v for k, v in h3_elem.attrs.items()}}
        )
        links = dl_elem.find_all("a", recursive=False)
        h3_obj["links"] = [self._parse_a_href(a) for a in links]
        return h3_obj

    def _get_dl_children(self, dl_elem):
        """Get child DL elements (subfolders)."""
        dl_elem_children = dl_elem.find_all("dl", recursive=False)
        return dl_elem_children

    def _parse_dl(self, dl_elem):
        """Recursively parse a DL element and its children."""
        dl_children = self._get_dl_children(dl_elem)
        return {
            **self._parse_dl_elem(dl_elem),
            "children": [self._parse_dl(dl_child) for dl_child in dl_children],
        }

    def _clean_bookmarks_file(self):
        """Clean the bookmarks file by removing <p> and <DT> tags."""
        from datetime import datetime

        tmpfname = f"tmp{round(datetime.now().timestamp())}.html"
        tmp_path = self.file_path.parent.joinpath(tmpfname)

        with open(self.file_path, "r", encoding="utf-8") as fin, open(
            tmp_path, "w+", encoding="utf-8"
        ) as fout:
            for line in fin:
                fout.write(line.replace("<p>", "").replace("<DT>", ""))

        return tmp_path
