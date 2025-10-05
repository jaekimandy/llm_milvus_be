"""
Download Qwen 2.5 GGUF model - Best for CPU + Korean language support
"""
import os
from huggingface_hub import hf_hub_download

def download_qwen25_gguf():
    """Download Qwen 2.5 GGUF model from Hugging Face"""
    # Qwen 2.5 7B Instruct GGUF - optimized for CPU inference with Korean support
    model_repo = "bartowski/Qwen2.5-7B-Instruct-GGUF"

    # Q4_K_M is recommended for most CPUs (good balance)
    model_file = "Qwen2.5-7B-Instruct-Q4_K_M.gguf"

    cache_dir = "./models/qwen2.5-gguf"

    print(f"Downloading Qwen 2.5 7B Instruct GGUF from {model_repo}...")
    print(f"Cache directory: {cache_dir}")
    print(f"Model file: {model_file}")

    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)

    try:
        print("\nDownloading Qwen 2.5 7B Instruct Q4_K_M (recommended for CPU)...")
        file_path = hf_hub_download(
            repo_id=model_repo,
            filename=model_file,
            cache_dir=cache_dir,
            resume_download=True
        )

        print(f"\n[SUCCESS] Qwen 2.5 downloaded successfully!")
        print(f"File location: {file_path}")
        print(f"\nModel info:")
        print(f"  - Size: ~4.4GB (Q4_K_M quantization)")
        print(f"  - Context: 32K tokens")
        print(f"  - Languages: Multilingual (excellent Korean support)")
        print(f"  - Optimized for: CPU inference")

        return True

    except Exception as e:
        print(f"[ERROR] Error downloading Qwen 2.5: {e}")
        print(f"\nAvailable quantizations:")
        print(f"  - Q4_K_M (4-bit, ~4.4GB) - Recommended")
        print(f"  - Q5_K_M (5-bit, ~5.3GB)")
        print(f"  - Q6_K (6-bit, ~6.3GB)")
        print(f"  - Q8_0 (8-bit, ~8.1GB)")
        return False

if __name__ == "__main__":
    download_qwen25_gguf()
