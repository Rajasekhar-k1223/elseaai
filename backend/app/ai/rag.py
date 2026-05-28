import uuid
from qdrant_client import AsyncQdrantClient
from qdrant_client import models as qmodels
from app.core.config import settings

class RAGService:
    def __init__(self):
        self.qdrant = AsyncQdrantClient(url=settings.QDRANT_URL)
        self.collection_name = "elsea_documents"

    async def ensure_collection(self, vector_size: int = 768):
        collections = await self.qdrant.get_collections()
        if self.collection_name not in [c.name for c in collections.collections]:
            await self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
            )

    async def index_document_chunk(self, chunk_text: str, embedding: list[float], metadata: dict):
        point_id = str(uuid.uuid4())
        await self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[
                qmodels.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={"text": chunk_text, **metadata}
                )
            ]
        )

    async def retrieve_context(self, query_embedding: list[float], limit: int = 3) -> list[str]:
        search_result = await self.qdrant.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=limit
        )
        contexts = [hit.payload["text"] for hit in search_result.points if hit.payload and "text" in hit.payload]
        return contexts

rag_service = RAGService()
