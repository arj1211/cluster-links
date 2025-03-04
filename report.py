import collections
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def extract_keywords_from_text(text, top_n=5):
    # Advanced keyword extraction: using unigrams and bigrams.
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000, ngram_range=(1,2), min_df=1)
    try:
        tfidf = vectorizer.fit_transform([text])
        feature_array = np.array(vectorizer.get_feature_names_out())
        tfidf_sorting = np.argsort(tfidf.toarray()).flatten()[::-1]
        top_n_keywords = feature_array[tfidf_sorting][:top_n]
        return ", ".join(top_n_keywords)
    except Exception as e:
        return "N/A"

def generate_cluster_report(urls, texts, labels, output_file="cluster_report.txt"):
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
