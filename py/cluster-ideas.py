#!/usr/bin/env python3
"""
Cluster and Summarize Text Responses Using Machine Learning

This script uses natural language processing and machine learning to automatically
group similar text responses into clusters. It reads responses from a file, converts
them to numerical embeddings using a transformer model, clusters them with K-Means,
and provides summaries of each cluster showing common themes and example responses.

Usage: python3 cluster-ideas.py -f <input_file>
"""

import numpy as np
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import matplotlib.pyplot as plt
import argparse
from collections import defaultdict
import nltk
from collections import Counter

# Ensure NLTK punkt tokenizer is downloaded
nltk.download("punkt")

# Step 1: Setup argument parser for command-line flags
parser = argparse.ArgumentParser(
    description="Cluster and summarize responses from a file."
)
parser.add_argument(
    "-f", "--file", required=True, help="Path to the input file containing responses"
)

# Parse the arguments
args = parser.parse_args()

# Step 2: Read the responses from the file
with open(args.file, "r") as file:
    responses = [line.strip() for line in file.readlines() if line.strip()]

# Step 3: Generate embeddings using a pretrained transformer model
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)  # Efficient and lightweight sentence transformer model
embeddings = model.encode(responses)


# Step 4: Choose the number of clusters using the Elbow method (optional)
def find_optimal_clusters(embeddings, max_k=10):
    iters = range(2, max_k + 1)
    sse = []
    for k in iters:
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(embeddings)
        sse.append(
            kmeans.inertia_
        )  # Sum of squared distances of samples to their closest cluster center

    # Plot to visualize the elbow point
    plt.plot(iters, sse, marker="o")
    plt.xlabel("Number of clusters")
    plt.ylabel("SSE (Sum of squared distances)")
    plt.title("Elbow Method for Optimal Clusters")
    plt.show()


# Uncomment to plot and find optimal clusters visually
# find_optimal_clusters(embeddings)

# Step 5: Cluster using KMeans with an appropriate number of clusters (from elbow or silhouette method)
n_clusters = 5  # You can adjust this based on elbow method findings
kmeans = KMeans(n_clusters=n_clusters)
kmeans.fit(embeddings)

# Step 6: Assign each response to a cluster
cluster_labels = kmeans.labels_

# Step 7: Group responses by their clusters
clustered_responses = defaultdict(list)
for i, label in enumerate(cluster_labels):
    clustered_responses[label].append(responses[i])


# Step 8: Summarize each cluster by printing a few example responses and common terms
def summarize_cluster(cluster_responses):
    print("\nCluster Summary:")
    # Print example responses
    print("\nExample Responses:")
    for response in cluster_responses[:3]:  # Show a few examples
        print(f"- {response}")

    # Get frequent terms using word frequency analysis
    all_words = nltk.word_tokenize(" ".join(cluster_responses).lower())
    word_freq = Counter([word for word in all_words if word.isalnum()])

    # Print common terms (excluding very common words like 'the', 'and', etc.)
    common_words = [word for word, freq in word_freq.most_common(10)]
    print(f"\nCommon terms: {', '.join(common_words)}")


# Step 9: Summarize all clusters
for cluster_id, cluster_responses in clustered_responses.items():
    print(f"\n--- Cluster {cluster_id + 1} ---")
    summarize_cluster(cluster_responses)
