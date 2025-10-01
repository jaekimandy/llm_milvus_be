from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.embeddings.base import Embeddings
from config.settings import settings
from typing import List, Dict, Any
import voyageai


class VoyageEmbeddings(Embeddings):
    """Voyage AI embeddings wrapper for LangChain"""

    def __init__(self, api_key: str, model: str = "voyage-3"):
        self.client = voyageai.Client(api_key=api_key)
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        result = self.client.embed(texts, model=self.model)
        return result.embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        result = self.client.embed([text], model=self.model)
        return result.embeddings[0]

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Async embed documents"""
        return self.embed_documents(texts)

    async def aembed_query(self, text: str) -> List[float]:
        """Async embed query"""
        return self.embed_query(text)


class LLMClient:
    """LLM client wrapper supporting both Claude (Anthropic) and OpenAI"""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()

        # Initialize chat model based on provider
        if self.provider == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY is required when LLM_PROVIDER is 'anthropic'")

            self.chat_model = ChatAnthropic(
                model=settings.ANTHROPIC_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                anthropic_api_key=settings.ANTHROPIC_API_KEY
            )
        elif self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER is 'openai'")

            self.chat_model = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                openai_api_key=settings.OPENAI_API_KEY
            )
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: {self.provider}. Use 'anthropic' or 'openai'")

        # Initialize embeddings based on provider
        embeddings_provider = settings.EMBEDDINGS_PROVIDER.lower()

        if embeddings_provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required when EMBEDDINGS_PROVIDER is 'openai'")
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY
            )
            print("✓ Using OpenAI embeddings")
        elif embeddings_provider == "voyage":
            if not settings.VOYAGE_API_KEY:
                raise ValueError("VOYAGE_API_KEY is required when EMBEDDINGS_PROVIDER is 'voyage'")
            self.embeddings = VoyageEmbeddings(
                api_key=settings.VOYAGE_API_KEY,
                model=settings.VOYAGE_MODEL
            )
            print(f"✓ Using Voyage AI embeddings: {settings.VOYAGE_MODEL}")
        else:
            raise ValueError(f"Unsupported EMBEDDINGS_PROVIDER: {embeddings_provider}. Use 'openai' or 'voyage'")

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None
    ) -> str:
        """Generate response from LLM"""
        formatted_messages = []

        if system_prompt:
            formatted_messages.append(SystemMessage(content=system_prompt))

        for msg in messages:
            if msg["role"] == "user":
                formatted_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                formatted_messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                formatted_messages.append(SystemMessage(content=msg["content"]))

        response = await self.chat_model.ainvoke(formatted_messages)
        return response.content

    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        if not self.embeddings:
            raise ValueError("Embeddings provider not configured. Set OPENAI_API_KEY in .env")

        embeddings = await self.embeddings.aembed_query(text)
        return embeddings

    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not self.embeddings:
            raise ValueError("Embeddings provider not configured. Set OPENAI_API_KEY in .env")

        embeddings = await self.embeddings.aembed_documents(texts)
        return embeddings


# Singleton instance
llm_client = LLMClient()
