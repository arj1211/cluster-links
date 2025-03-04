import numpy as np
import hdbscan
from sklearn.cluster import AgglomerativeClustering

def cluster_embeddings(embeddings, min_cluster_size=2, min_samples=1):
    """Cluster the embeddings using HDBSCAN."""
    if min_cluster_size < 2:
        min_cluster_size = 2  # HDBSCAN requires a min_cluster_size > 1.
    if isinstance(embeddings, list):
        embeddings = np.array(embeddings)
    if embeddings.ndim == 1:
        embeddings = embeddings.reshape(-1, 1)
    if embeddings.shape[0] == 0:
        print("No embeddings available to cluster.")
        return []
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples, metric='euclidean')
    labels = clusterer.fit_predict(embeddings)
    return labels

def hierarchical_clustering(embeddings, distance_threshold=1.5):
    """Perform hierarchical clustering (Agglomerative) and return the labels."""
    if isinstance(embeddings, list):
        embeddings = np.array(embeddings)
    if embeddings.ndim == 1:
        embeddings = embeddings.reshape(-1, 1)
    if embeddings.shape[0] == 0:
        print("No embeddings available for hierarchical clustering.")
        return []
    clustering = AgglomerativeClustering(distance_threshold=distance_threshold, n_clusters=None, linkage="ward")
    clustering.fit(embeddings)
    return clustering.labels_
