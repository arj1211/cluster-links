import collections

from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

# Initialize KeyBERT with an SBERT model.
kw_model = KeyBERT(model=SentenceTransformer("all-MiniLM-L6-v2"))


def extract_keywords_from_text(text: str, top_n: int = 5) -> str:
    """Extracts semantic keywords using KeyBERT."""
    try:
        keywords = kw_model.extract_keywords(
            text, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=top_n
        )
        # Return a comma-separated string of the keywords.
        return ", ".join([kw[0] for kw in keywords])
    except Exception as e:
        return "N/A"


def generate_cluster_report(
    urls: list[str],
    texts: list[str],
    labels: list[int],
    output_file: str = "cluster_report.txt",
):
    cluster_data = collections.defaultdict(list)
    for url, text, label in zip(urls, texts, labels):
        cluster_data[label].append((url, text))
    with open(output_file, "w", encoding="utf-8") as f:
        for cluster, items in sorted(cluster_data.items()):
            combined_text = " ".join(text for url, text in items)
            keywords = extract_keywords_from_text(combined_text)
            f.write(f"Cluster {cluster} ({len(items)} items) - Keywords: {keywords}\n")
            for url, text in items:
                snippet = text[:200].replace("\n", " ")
                f.write(f"  - {url}\n    {snippet}...\n")
            f.write("\n")
    print(f"Cluster report generated and saved to {output_file}")
