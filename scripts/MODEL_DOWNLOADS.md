# Model Downloads Summary

## Overview
This document tracks the models downloaded for the SKCC GAIA ABIZ Backend project.

## Downloaded Models

### 1. Jina Embeddings v3 ✅ COMPLETED
- **Repository**: `jinaai/jina-embeddings-v3`
- **Location**: `scripts/models/jina-embeddings-v3/`
- **Size**: ~1.1GB (safetensors) + ~1.1GB (pytorch)
- **Purpose**: Text embeddings for RAG (Retrieval Augmented Generation)
- **Features**:
  - High-quality multilingual embeddings
  - Support for long context (8192 tokens)
  - Excellent for semantic search and retrieval
- **Download Script**: `download_jina_embeddings.py`
- **Status**: Successfully downloaded

### 2. Qwen 2.5 7B Instruct GGUF ⏳ IN PROGRESS
- **Repository**: `bartowski/Qwen2.5-7B-Instruct-GGUF`
- **Model File**: `Qwen2.5-7B-Instruct-Q4_K_M.gguf`
- **Location**: `scripts/models/qwen2.5-gguf/`
- **Size**: ~4.4GB (Q4_K_M quantization)
- **Purpose**: CPU-optimized LLM for Korean language support
- **Features**:
  - Excellent Korean language support
  - 32K context window
  - Optimized for CPU inference (GGUF format)
  - Q4_K_M quantization for balance between quality and speed
- **Download Script**: `download_qwen2.5.py`
- **Status**: Currently downloading

## Download Scripts Location
All download scripts are located in: `gaia-abiz-backend/scripts/`

## Running the Scripts
```bash
cd gaia-abiz-backend/scripts

# Download Jina Embeddings v3
python download_jina_embeddings.py

# Download Qwen 2.5 7B GGUF
python download_qwen2.5.py
```

## Using the Models

### Jina Embeddings v3
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    './models/jina-embeddings-v3',
    trust_remote_code=True
)

# Generate embeddings
embeddings = model.encode(['Your text here'])
```

### Qwen 2.5 (with llama.cpp or similar)
```python
from llama_cpp import Llama

llm = Llama(
    model_path='./models/qwen2.5-gguf/Qwen2.5-7B-Instruct-Q4_K_M.gguf',
    n_ctx=32768,  # Context window
    n_threads=8   # CPU threads
)

response = llm('Your prompt here')
```

## Notes
- All models are optimized for CPU inference
- Jina Embeddings v3 is ideal for embedding generation in RAG pipelines
- Qwen 2.5 provides excellent Korean language understanding and generation
- Models are cached locally to avoid re-downloading

## Date
Downloaded: October 5, 2025
