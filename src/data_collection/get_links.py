from pathlib import Path


def get_links(file_path: str) -> list[str]:
    """
    Read a file containing links (one per line or in markdown format) and
    return a list of URLs that contain 'http'. Extracts the URL starting
    from the first occurrence of 'http' on each line.
    """
    path = Path(file_path).expanduser()
    print(f"Reading links from {path}")

    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    links = [line[line.find("http") :].strip() for line in lines if "http" in line]
    return links


if __name__ == "__main__":
    from config import load_config

    config = load_config()  # Loads config.json
    file_path = config.get("LINKS_FILE", "links.txt")
    links = get_links(file_path)
    print("Extracted links:")
    for link in links:
        print(link)
