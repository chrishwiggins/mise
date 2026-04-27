import plotly.express as px

# PLOT DIMENSIONS - Adjust these to change plot size
PLOT_WIDTH = 1200   # pixels (try 800-1600)
PLOT_HEIGHT = 800   # pixels (try 600-1000)

print("\n INTERACTIVE SCATTER PLOT (using Plotly)")
print("-" * 60)

if TRANSFORMERS_AVAILABLE and len(texts) >= 2:
    try:
        # Create a DataFrame for Plotly
        plot_df = pd.DataFrame({
            'PC1': embeddings_2d[:, 0],
            'PC2': embeddings_2d[:, 1],
            'Year': labels,
            'Interest_Text': texts
        })

        # Create interactive scatter plot
        fig = px.scatter(plot_df,
                         x='PC1',
                         y='PC2',
                         color='Year',
                         hover_data={'Interest_Text': True, 'PC1': False, 'PC2': False},
                         title='Transformer Embeddings: Your Survey Data (Interactive)')

        fig.update_layout(
            xaxis_title=f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)',
            yaxis_title=f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)',
            width=PLOT_WIDTH,
            height=PLOT_HEIGHT
        )

        fig.show()

        print(f"\n Interactive Plot created:")
        print(f"   Hover over points to see the full interest text.")
        print(f"   Plot dimensions: {PLOT_WIDTH}x{PLOT_HEIGHT} pixels")

    except Exception as e:
        print(f" Plotly interactive plot failed: {e}")
        print("   (Ensure Plotly is installed and Colab environment supports interactive plots)")

else:
     print(" Transformer embeddings not available or insufficient data for Plotly plot.")