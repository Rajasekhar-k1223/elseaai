from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from app.ai.ollama import llm_client
from app.ai.embeddings import embedding_client
from app.ai.rag import rag_service
from app.api.deps import get_current_user
from app.models.user import User
from app.db.mongodb import mongodb
from bson import ObjectId
import json
from datetime import datetime

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    thread_id: Optional[str] = None
    message: str
    model: str = "llama3.2"

@router.post("/stream")
async def chat_stream(request: ChatRequest, current_user: User = Depends(get_current_user)):
    db = mongodb.db
    messages_history = []
    thread_id_obj = None

    if request.thread_id:
        try:
            thread_id_obj = ObjectId(request.thread_id)
            thread = await db.threads.find_one({"_id": thread_id_obj, "user_id": current_user.id})
            if not thread:
                raise HTTPException(status_code=404, detail="Thread not found")
            messages_history = thread.get("messages", [])
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid thread ID")
    else:
        # Create new thread
        result = await db.threads.insert_one({
            "user_id": current_user.id,
            "title": request.message[:30] + "...",
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        thread_id_obj = result.inserted_id

    # Append user message
    user_msg = {"role": "user", "content": request.message, "timestamp": datetime.utcnow()}
    await db.threads.update_one(
        {"_id": thread_id_obj},
        {"$push": {"messages": user_msg}, "$set": {"updated_at": datetime.utcnow()}}
    )
    
    messages_history.append({"role": "user", "content": request.message})

    # Prepare for Ollama (strip timestamp)
    ollama_messages = [{"role": m["role"], "content": m["content"]} for m in messages_history]

    # --- RAG Retrieval ---
    try:
        query_embedding = await embedding_client.generate_embedding(request.message)
        context_chunks = await rag_service.retrieve_context(query_embedding, limit=3)
        if context_chunks:
            context_str = "\n\n---\n\n".join(context_chunks)
            system_prompt = (
                f"You are ElseaAI, an enterprise AI assistant. Use the following retrieved document context "
                f"to answer the user's question accurately. If the context does not contain the answer, "
                f"say so.\n\nContext:\n{context_str}"
            )
            
            if ollama_messages and ollama_messages[0]["role"] != "system":
                ollama_messages.insert(0, {"role": "system", "content": system_prompt})
            elif ollama_messages and ollama_messages[0]["role"] == "system":
                ollama_messages[0]["content"] += f"\n\nContext for current query:\n{context_str}"
    except Exception as e:
        print(f"RAG Retrieval failed: {e}")
    # ---------------------

    async def stream_and_save():
        full_response = ""
        async for chunk in llm_client.chat_stream(messages=ollama_messages, model=request.model):
            full_response += chunk
            yield chunk
            
        # Save assistant response
        assistant_msg = {"role": "assistant", "content": full_response, "timestamp": datetime.utcnow()}
        await db.threads.update_one(
            {"_id": thread_id_obj},
            {"$push": {"messages": assistant_msg}, "$set": {"updated_at": datetime.utcnow()}}
        )

    return StreamingResponse(stream_and_save(), media_type="text/event-stream")
