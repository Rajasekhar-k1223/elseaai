import os
from huggingface_hub import hf_hub_download

# We'll use a tiny, fast model: Qwen2.5 0.5B Instruct (GGUF format)
# Perfect for CPU or M1/M2 Mac inference.
repo_id = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
filename = "qwen2.5-0.5b-instruct-q4_k_m.gguf"

print(f"Downloading {filename} from HuggingFace ({repo_id})...")
print("This may take a few minutes depending on your internet connection.")

model_path = hf_hub_download(
    repo_id=repo_id,
    filename=filename,
    local_dir=".",
    local_dir_use_symlinks=False
)

print(f"Download complete! Model saved to: {model_path}")
