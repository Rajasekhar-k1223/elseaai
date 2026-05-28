import json
import httpx
from typing import AsyncGenerator
from app.core.config import settings

class LLMClient:
    def __init__(self):
        self.ollama_base = settings.OLLAMA_URL
        self.ollama_chat_url = f"{self.ollama_base}/api/chat"
        
        self.groq_api_key = settings.GROQ_API_KEY
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.custom_server_url = "http://host.docker.internal:8001/v1/chat/completions"
        
    async def chat_stream(self, messages: list[dict], model: str = "llama3.2") -> AsyncGenerator[str, None]:
        
        # Route to Custom AI Server if selected
        if model.lower() == "custom":
            payload = {
                "model": "custom",
                "messages": messages,
                "stream": True
            }
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", self.custom_server_url, json=payload, timeout=120.0) as response:
                    if response.status_code != 200:
                        yield f"Error: Failed to connect to Custom AI Server ({response.status_code}). Is the python server running on port 8001?"
                        return
                    
                    async for chunk in response.aiter_lines():
                        if chunk.startswith("data: "):
                            data_str = chunk[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
            return

        # Switch to Groq if the user selected a Groq model or if Groq API key is configured
        # Note: If no groq key is provided, we must fallback to ollama.
        is_cloud = bool(self.groq_api_key) and ("qwen" not in model.lower())
        
        if is_cloud:
            # Overwrite model if it's generic
            if model == "llama3.2" or model == "deepseek":
                model = "llama-3.3-70b-versatile" # Groq's blazing fast model

            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": messages,
                "stream": True
            }
            
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", self.groq_url, json=payload, headers=headers, timeout=120.0) as response:
                    if response.status_code != 200:
                        yield f"Error: Failed to connect to Groq API ({response.status_code}). Did you provide a valid API Key?"
                        return
                    
                    async for chunk in response.aiter_lines():
                        if chunk.startswith("data: "):
                            data_str = chunk[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
        else:
            # Fallback to Ollama
            payload = {
                "model": model,
                "messages": messages,
                "stream": True
            }
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", self.ollama_chat_url, json=payload, timeout=120.0) as response:
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

llm_client = LLMClient()
