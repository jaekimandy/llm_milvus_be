"""
Download Jina Embeddings v3 model
"""
import os
from sentence_transformers import SentenceTransformer

def download_jina_embeddings_v3():
    """Download Jina Embeddings v3 model from Hugging Face"""
    model_name = "jinaai/jina-embeddings-v3"
    cache_dir = "./models/jina-embeddings-v3"

    print(f"Downloading Jina Embeddings v3 from {model_name}...")
    print(f"Cache directory: {cache_dir}")

    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)

    try:
        # Download model using SentenceTransformer
        print("Downloading model with SentenceTransformer...")
        model = SentenceTransformer(
            model_name,
            cache_folder=cache_dir,
            trust_remote_code=True
        )

        print(f"[SUCCESS] Successfully downloaded Jina Embeddings v3 to {cache_dir}")
        return True

    except Exception as e:
        print(f"[ERROR] Error downloading Jina Embeddings v3: {e}")
        return False

if __name__ == "__main__":
    download_jina_embeddings_v3()
