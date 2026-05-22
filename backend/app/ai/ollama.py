import json
import httpx
from typing import AsyncGenerator
from app.core.config import settings

class OllamaClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.generate_url = f"{self.base_url}/api/generate"
        self.chat_url = f"{self.base_url}/api/chat"

    async def generate_stream(self, prompt: str, model: str = "llama3.2") -> AsyncGenerator[str, None]:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", self.generate_url, json=payload, timeout=60.0) as response:
                if response.status_code != 200:
                    yield f"Error: Failed to connect to Ollama ({response.status_code})"
                    return
                
                async for chunk in response.aiter_lines():
                    if chunk:
                        try:
                            data = json.loads(chunk)
                            if "response" in data:
                                yield data["response"]
                        except json.JSONDecodeError:
                            continue

    async def chat_stream(self, messages: list[dict], model: str = "llama3.2") -> AsyncGenerator[str, None]:
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", self.chat_url, json=payload, timeout=120.0) as response:
                if response.status_code != 200:
                    yield f"Error: Failed to connect to Ollama ({response.status_code})"
                    return
                
                async for chunk in response.aiter_lines():
                    if chunk:
                        try:
                            data = json.loads(chunk)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                        except json.JSONDecodeError:
                            continue

ollama_client = OllamaClient()
