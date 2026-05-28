import os
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import List, Optional
import time

try:
    from llama_cpp import Llama
except ImportError:
    print("CRITICAL: llama-cpp-python is not installed. Please run: pip install -r requirements.txt")
    exit(1)

app = FastAPI(title="Custom AI Runtime Server")

# Allow requests from anywhere (like the ElseaAI backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MODEL_PATH = os.environ.get("MODEL_PATH", "qwen2.5-0.5b-instruct-q4_k_m.gguf")
N_CTX = 4096
N_GPU_LAYERS = -1 # -1 means offload all layers to GPU (Metal/CUDA) if available!

print(f"Loading model {MODEL_PATH}...")
try:
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=N_CTX,
        n_gpu_layers=N_GPU_LAYERS,
        verbose=False
    )
    print("Model loaded successfully!")
except Exception as e:
    print(f"Failed to load model: {e}")
    print(f"Please ensure {MODEL_PATH} exists in this directory. Run download_model.py first!")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "custom"
    messages: List[ChatMessage]
    stream: bool = False
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_PATH}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request, body: ChatCompletionRequest):
    # Convert messages to ChatML format for Qwen
    formatted_messages = [{"role": m.role, "content": m.content} for m in body.messages]
    
    if not body.stream:
        # Synchronous response
        response = llm.create_chat_completion(
            messages=formatted_messages,
            temperature=body.temperature,
            max_tokens=body.max_tokens,
            stream=False
        )
        return response

    # Streaming response
    async def event_generator():
        stream = llm.create_chat_completion(
            messages=formatted_messages,
            temperature=body.temperature,
            max_tokens=body.max_tokens,
            stream=True
        )
        
        for chunk in stream:
            # We must yield bytes or strings for EventSourceResponse
            if await request.is_disconnected():
                break
                
            yield {
                "event": "message",
                "data": json.dumps(chunk)
            }
            # Add a tiny sleep to allow the async event loop to breathe
            await asyncio.sleep(0.001)
            
        yield {
            "event": "message",
            "data": "[DONE]"
        }

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    print("\nStarting Custom AI Server on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
