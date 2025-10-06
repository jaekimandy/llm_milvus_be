"""
Download MPNet Embeddings model
"""
import os
from sentence_transformers import SentenceTransformer

def download_mpnet_embeddings():
    """Download MPNet Embeddings model from Hugging Face"""
    model_name = "sentence-transformers/all-mpnet-base-v2"
    cache_dir = "./models/all-mpnet-base-v2"

    print(f"Downloading MPNet Embeddings from {model_name}...")
    print(f"Cache directory: {cache_dir}")

    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)

    try:
        # Download model using SentenceTransformer
        print("Downloading model with SentenceTransformer...")
        model = SentenceTransformer(
            model_name,
            cache_folder=cache_dir
        )

        print(f"[SUCCESS] Successfully downloaded MPNet Embeddings to {cache_dir}")
        return True

    except Exception as e:
        print(f"[ERROR] Error downloading MPNet Embeddings: {e}")
        return False

if __name__ == "__main__":
    download_mpnet_embeddings()
