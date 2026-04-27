try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print(" Sentence-transformers not available - install for demo")

print("\n THE TRANSFORMER ERA (2017-2024)")
print("=" * 60)
print(" PART 5: ATTENTION IS ALL YOU NEED")
print("-" * 40)

print(" Historical Context:")
print("   • Vaswani et al. (2017): 'Attention Is All You Need'")
print("   • BERT (2018), GPT (2018): Transformer applications")
print("   • Current: GPT-4, Claude, ChatGPT all use transformer architecture")

print("\n Mathematical Core (Chalk Sketch):")
print("   Attention: A(Q,K,V) = softmax(QK^T/√d_k)V")
print("   Multi-head: Concat(head_1, ..., head_h)W^O")
print("   Key innovation: Self-attention mechanism")

print("\n Revolutionary Capabilities:")
print("   • Contextual understanding (not just word-level)")
print("   • Long-range dependencies")
print("   • Transfer learning from massive corpora")
print("   • Few-shot learning")

if TRANSFORMERS_AVAILABLE:
    try:
        print(f"\n Loading Pre-trained Transformer...")
        print(f"   Model: all-MiniLM-L6-v2 (384-dimensional)")
        print(f"   Training: 1B+ sentence pairs")

        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Encode documents
        texts = []
        labels = []
        for _, row in df.iterrows():
            text = row['interests_clean'].strip()
            if len(text) > 10:
                texts.append(text)
                labels.append(row['year'])

        if len(texts) >= 2:
            print(f" Model loaded! Encoding {len(texts)} documents...")
            embeddings = model.encode(texts, show_progress_bar=False)

            print(f"   Embeddings shape: {embeddings.shape}")
            print(f"   Each document -> 384-dimensional vector")

            # Analyze semantic similarities
            from sklearn.metrics.pairwise import cosine_similarity
            sim_matrix = cosine_similarity(embeddings)

            upper_tri = np.triu_indices_from(sim_matrix, k=1)
            similarities = sim_matrix[upper_tri]

            print(f"\n Transformer Semantic Analysis:")
            print(f"   Mean similarity: {np.mean(similarities):.3f}")
            print(f"   Similarity std: {np.std(similarities):.3f}")

            # Find most semantically similar documents
            if len(similarities) > 0:
                max_sim_idx = np.argmax(similarities)
                i, j = upper_tri[0][max_sim_idx], upper_tri[1][max_sim_idx]
                max_sim = similarities[max_sim_idx]

                print(f"\n Most Semantically Similar (cosine = {max_sim:.3f}):")
                print(f"   [{labels[i]}]: {texts[i][:60]}...")
                print(f"   [{labels[j]}]: {texts[j][:60]}...")

            # Dimensionality reduction for visualization
            from sklearn.decomposition import PCA
            pca = PCA(n_components=2, random_state=42)
            embeddings_2d = pca.fit_transform(embeddings)

            print(f"\n Transformer Advantages:")
            print(f"   • Captures context, not just individual words")
            print(f"   • Pre-trained on massive text corpora")
            print(f"   • Works well even with small datasets (like ours)")
            print(f"   • Foundation for modern AI applications")

        else:
            print(" Need more text samples for transformer demo")

    except Exception as e:
        print(f" Transformer demo failed: {e}")
        print("   (May need internet connection for model download)")

else:
    print(" Transformer Pseudocode (Vaswani 2017):")
    print("   def attention(Q, K, V):")
    print("     scores = Q @ K.T / sqrt(d_k)")
    print("     weights = softmax(scores)")
    print("     return weights @ V")
    print("   ")
    print("   # Multi-head attention allows different types of relationships")
    print("   # Self-attention: each word attends to all other words")