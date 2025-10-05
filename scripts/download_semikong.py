"""
Download SemiKong model
"""
import os
from transformers import AutoModel, AutoTokenizer

def download_semikong():
    """Download SemiKong model from Hugging Face"""
    # SemiKong is a Korean language model - using the most common variant
    model_name = "beomi/SemiKong-v1-Korean"
    cache_dir = "./models/semikong"

    print(f"Downloading SemiKong from {model_name}...")
    print(f"Cache directory: {cache_dir}")

    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)

    try:
        # Download tokenizer
        print("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            trust_remote_code=True
        )

        # Download model
        print("Downloading model...")
        model = AutoModel.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            trust_remote_code=True
        )

        print(f"[SUCCESS] Successfully downloaded SemiKong to {cache_dir}")
        return True

    except Exception as e:
        print(f"[ERROR] Error downloading SemiKong: {e}")
        print(f"Note: If the model name is incorrect, please specify the correct Hugging Face model ID")
        return False

if __name__ == "__main__":
    download_semikong()
