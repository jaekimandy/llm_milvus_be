from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from typing import List, Dict, Any
from config.settings import settings


class VectorStore:
    """Milvus vector database client"""

    def __init__(self):
        self.host = settings.MILVUS_HOST
        self.port = settings.MILVUS_PORT
        self.collection_name = settings.MILVUS_COLLECTION_NAME
        self.collection = None

    def connect(self):
        """Connect to Milvus"""
        connections.connect(
            alias="default",
            host=self.host,
            port=str(self.port)
        )

    def create_collection(self, dim: int = 1536):
        """Create collection if it doesn't exist"""
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            return

        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535),
        ]

        schema = CollectionSchema(
            fields=fields,
            description="GaiA embeddings collection"
        )

        self.collection = Collection(
            name=self.collection_name,
            schema=schema
        )

        # Create index
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        self.collection.create_index(
            field_name="embedding",
            index_params=index_params
        )

    def insert(
        self,
        embeddings: List[List[float]],
        texts: List[str],
        metadata: List[str]
    ):
        """Insert embeddings into collection"""
        if not self.collection:
            raise ValueError("Collection not initialized")

        entities = [
            embeddings,
            texts,
            metadata
        ]

        self.collection.insert(entities)
        self.collection.flush()

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_expr: str = None
    ) -> List[Dict[str, Any]]:
        """Search for similar embeddings"""
        if not self.collection:
            raise ValueError("Collection not initialized")

        self.collection.load()

        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }

        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=filter_expr,
            output_fields=["text", "metadata"]
        )

        output = []
        for hits in results:
            for hit in hits:
                output.append({
                    "id": hit.id,
                    "distance": hit.distance,
                    "text": hit.entity.get("text"),
                    "metadata": hit.entity.get("metadata")
                })

        return output

    def delete(self, expr: str):
        """Delete entities by expression"""
        if not self.collection:
            raise ValueError("Collection not initialized")

        self.collection.delete(expr)

    def close(self):
        """Close connection"""
        connections.disconnect("default")


# Singleton instance
vector_store = VectorStore()
