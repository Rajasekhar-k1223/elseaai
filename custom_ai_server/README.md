# Custom AI Runtime Server

This is your custom-built inference server! It perfectly replicates Ollama's ability to run AI models offline, but gives you complete programmatic control.

## How to Run it on your Mac Mini M2
Because you have an M2 Mac, you have access to Apple's Unified Memory (Metal), which is INCREDIBLY fast. To install the engine specifically for the M2 chip, run these exact commands in your Mac terminal:

```bash
# 1. Install the high-speed Apple Metal version of the engine
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python

# 2. Install the web server components
pip install fastapi uvicorn sse-starlette huggingface-hub pydantic

# 3. Download the actual Brain (Qwen 2.5 0.5B model)
python download_model.py

# 4. Start the server!
python server.py
```

Once it says "Starting Custom AI Server on http://localhost:8001", you can go back into ElseaAI's chat, select "Custom AI Server" from the dropdown, and chat instantly!
