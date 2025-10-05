"""
Local LLM Client for Qwen 2.5 and Local Embeddings
Supports CPU-only inference with llama-cpp-python
"""
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from config.settings import settings
from typing import List, Dict, Any
import os


class LLMClient:
    """Local LLM client wrapper for Qwen 2.5 and HuggingFace embeddings"""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()

        if self.provider != "local":
            raise ValueError(f"Only 'local' provider is supported. Got: {self.provider}")

        # Initialize local embeddings
        print(f"Loading local embeddings: {settings.EMBEDDINGS_MODEL}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDINGS_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print(f"✓ Loaded embeddings model (dimension: {settings.EMBEDDINGS_DIMENSION})")

        # Initialize local LLM (lazy loading)
        self.chat_model = None
        self.model_path = settings.LLM_MODEL_PATH

        # Check if model file exists
        if not os.path.exists(self.model_path):
            print(f"⚠ Warning: LLM model not found at {self.model_path}")
            print("  LLM generation will not be available.")
            print("  Run: python scripts/download_qwen2.5.py")
        else:
            print(f"✓ LLM model ready at {self.model_path}")

    def _load_llm(self):
        """Lazy load LLM model (only when needed)"""
        if self.chat_model is not None:
            return

        try:
            from langchain_community.llms import LlamaCpp
            from langchain_community.llms.llamacpp import Callbacks

            print(f"Loading Qwen 2.5 model from {self.model_path}...")
            self.chat_model = LlamaCpp(
                model_path=self.model_path,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                n_ctx=settings.LLM_CONTEXT_LENGTH,
                n_threads=settings.LLM_N_THREADS,
                verbose=False,
            )
            print("✓ Qwen 2.5 model loaded successfully")
        except ImportError:
            raise ImportError(
                "llama-cpp-python is required for local LLM inference. "
                "Install with: pip install llama-cpp-python"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load LLM model: {e}")

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None
    ) -> str:
        """Generate response from local LLM"""
        self._load_llm()

        # Format messages into a prompt
        prompt_parts = []

        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}\n")

        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                prompt_parts.append(f"User: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}\n")
            elif role == "system":
                prompt_parts.append(f"System: {content}\n")

        prompt_parts.append("Assistant:")
        prompt = "\n".join(prompt_parts)

        # Generate response
        response = await self.chat_model.ainvoke(prompt)
        return response.strip()

    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        embeddings = await self.embeddings.aembed_query(text)
        return embeddings

    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = await self.embeddings.aembed_documents(texts)
        return embeddings


# Singleton instance
llm_client = LLMClient()
