import json
import shutil
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup


class ChromeBookmarkCollector:
    def __init__(self, bookmarks_html_file, pre_clean=True):
        self.bookmarks_html_file = bookmarks_html_file
        if pre_clean:
            self._clean_bookmarks_file()

        self.soup = BeautifulSoup(bookmarks_html_file.read_text(), "html.parser")
        self.root_element = self._get_root_dl()
        self.bookmarks = self._parse_dl(self.root_element)

    def get_bookmarks(self):
        return self.bookmarks

    def as_json(self):
        return json.dumps(self.bookmarks, indent=2)

    def _get_root_dl(self):
        dl_elements = self.soup.find_all("dl", recursive=False)
        assert len(dl_elements) == 1
        return dl_elements.pop()

    def _parse_a_href(self, a_href_elem):
        attrs = dict(a_href_elem.attrs)
        r_obj = {"title": " ".join(a_href_elem.text.replace("\n", "").split())}
        for k, v in attrs.items():
            r_obj[k] = v
        return r_obj

    def _parse_dl_elem(self, dl_elem):
        h3_elem = dl_elem.find_previous("h3", recursive=False)
        h3_obj = (
            {"title": "Unnamed"}
            if not h3_elem
            else {"title": h3_elem.text, **h3_elem.attrs}
        )
        links = dl_elem.find_all("a", recursive=False)
        h3_obj["links"] = [self._parse_a_href(a) for a in links]
        return h3_obj

    def _get_dl_children(self, dl_elem):
        dl_elem_children = dl_elem.find_all("dl", recursive=False)
        if not dl_elem_children:
            return []
        return dl_elem_children

    def _parse_dl(self, dl_elem):
        dl_children = self._get_dl_children(dl_elem)
        return {
            **self._parse_dl_elem(dl_elem),
            "children": [self._parse_dl(dl_child) for dl_child in dl_children],
        }

    def _clean_bookmarks_file(self):
        tmpfname = f"tmp{round(datetime.now().timestamp())}.html"
        with open(self.bookmarks_html_file, "r") as fin, open(
            self.bookmarks_html_file.parent.joinpath(tmpfname),
            "w+",
        ) as fout:
            for line in fin:
                fout.write(line.replace("<p>", "").replace("<DT>", ""))

        shutil.move(
            self.bookmarks_html_file.parent.joinpath(tmpfname), self.bookmarks_html_file
        )


if __name__ == "__main__":
    bookmarks_html_file = Path("data/input").glob("*.html").__next__()
    cbc = ChromeBookmarkCollector(bookmarks_html_file)
    with open("data/output/bookmarks.json", "w") as f:
        f.write(cbc.as_json())
    print("Bookmarks saved to data/output/bookmarks.json")
