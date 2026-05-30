import os
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import List, Optional
import time
import sys
sys.path.append(r"d:\sentinelx\sentinelx-sdk-python")
from sentinelx.client import SentinelXClient
from sentinelx.models import Heartbeat

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

# --- SentinelX Mesh Integration ---
ISOLATION_MODE = False

sentinel_client = SentinelXClient(
    base_url="http://localhost:8000",
    project_id="mi_ai_node",
    api_key="mock_secret_key_789"
)

async def handle_sentinel_commands(command: str, payload: dict):
    global ISOLATION_MODE
    if command == "GLOBAL_ISOLATION":
        print(f"🚨 SENTINELX C2 OVERRIDE: {payload.get('reason', 'Unknown threat')}")
        print("🚨 LOCKING DOWN AI ENDPOINTS.")
        ISOLATION_MODE = True

async def heartbeat_loop():
    while True:
        await sentinel_client.send_heartbeat(Heartbeat(status="healthy", active_connections=1))
        await asyncio.sleep(30)

@app.on_event("startup")
async def register_with_mesh():
    print("Registering MI-AI node with SentinelX Mesh...")
    if await sentinel_client.register_project() and await sentinel_client.authenticate():
        print("Successfully connected to SentinelX Mesh.")
        asyncio.create_task(sentinel_client.connect_websocket(handle_sentinel_commands))
        asyncio.create_task(heartbeat_loop())
    else:
        print("Failed to connect to SentinelX Mesh. Running standalone.")

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

from fastapi.responses import JSONResponse

@app.post("/v1/chat/completions")
async def chat_completions(request: Request, body: ChatCompletionRequest):
    global ISOLATION_MODE
    if ISOLATION_MODE:
        return JSONResponse(
            status_code=403, 
            content={"error": "MI-AI has been isolated by SentinelX due to an active network threat."}
        )

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
