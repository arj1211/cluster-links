import sys

from clustering import cluster_embeddings, hierarchical_clustering
from config import load_config
from extraction import get_embeddings, log_extraction_stats
from get_links import get_links
from report import generate_cluster_report


def main():
    config = load_config()  # Loads config.json
    links_file = config.get("LINKS_FILE", "links.txt")
    urls = get_links(links_file)
    if not urls:
        print("No URLs found. Exiting.")
        return
    rate_limiting_domains = config.get("RATE_LIMITING_DOMAINS", [])
    ignore_domains = config.get("IGNORE_DOMAINS", [])

    print("Fetching content and computing embeddings in parallel...")
    # Pass the rate limiting domains from config.
    embeddings, texts = get_embeddings(
        urls,
        max_workers=10,
        rate_limiting_domains=rate_limiting_domains,
        ignore_domains=ignore_domains,
    )

    log_extraction_stats()

    print("Clustering with HDBSCAN...")
    hdbscan_labels = cluster_embeddings(embeddings, min_cluster_size=2, min_samples=1)
    print("HDBSCAN Cluster labels:", hdbscan_labels)

    print("Clustering with Hierarchical Clustering...")
    hier_labels = hierarchical_clustering(embeddings, distance_threshold=1.5)
    print("Hierarchical Cluster labels:", hier_labels)

    print("Generating cluster reports...")
    generate_cluster_report(
        urls, texts, hdbscan_labels, output_file="hdbscan_cluster_report.txt"
    )
    generate_cluster_report(
        urls, texts, hier_labels, output_file="hierarchical_cluster_report.txt"
    )


if __name__ == "__main__":
    main()
