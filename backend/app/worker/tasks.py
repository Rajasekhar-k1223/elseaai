import asyncio
from app.worker.celery_app import celery_app
from app.ai.embeddings import embedding_client
from app.ai.rag import rag_service

from app.ai.chunking import text_splitter

@celery_app.task(name="app.worker.tasks.process_document")
def process_document_task(document_id: str, text: str, metadata: dict):
    # Celery tasks are synchronous by default, but we need to run async code.
    # We create a new event loop or use asyncio.run to execute the async embedding/indexing logic
    async def process():
        chunks = text_splitter.split_text(text)
        await rag_service.ensure_collection()
        for i, chunk in enumerate(chunks):
            chunk_metadata = {**metadata, "document_id": document_id, "chunk_index": i}
            embedding = await embedding_client.generate_embedding(chunk)
            await rag_service.index_document_chunk(chunk, embedding, chunk_metadata)
    
    asyncio.run(process())
    return {"status": "success", "document_id": document_id}
