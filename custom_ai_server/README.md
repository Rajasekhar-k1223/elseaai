# Custom AI Runtime Server for Apple Silicon (Mac M2)

This folder contains a fully offline, private AI inference server designed specifically to run at maximum speed on your Apple Mac M2 using the Metal GPU framework. It also includes the tools needed to fine-tune your own AI using your private health records.

## Pipeline Overview
1. **Format Data**: Convert health records to JSONL.
2. **Fine-Tune (MLX)**: Train a custom AI on your Mac M2 securely.
3. **Convert to GGUF**: Export the brain for inference.
4. **Run Server**: Serve it privately.

---

## Step 1: Format Your Health Records
We have provided `format_health_records.py`. This script converts a CSV of your health records into the `JSONL` format required by the AI.
1. Save your health records as `health_records.csv` with columns: `patient_symptoms`, `diagnosis`, `treatment`.
2. Run the script:
```bash
python format_health_records.py --input health_records.csv --output training_data.jsonl
```

---

## Step 2: Fine-Tune on Mac M2 (100% Private)
Because your data is sensitive, we will train the AI directly on your Mac using **Apple MLX** instead of the cloud. This ensures HIPAA/Privacy compliance.

1. **Install MLX**:
```bash
pip install mlx-lm
```
2. **Start the Fine-Tuning Process**:
This will take the base `Qwen2.5-0.5B` model and train it on your `training_data.jsonl`.
```bash
python -m mlx_lm.lora \
    --model Qwen/Qwen2.5-0.5B-Instruct \
    --train \
    --data ./ \
    --iters 1000 \
    --adapter-path my_medical_adapter
```
*(Make sure `training_data.jsonl` is renamed to `train.jsonl` or use the `--data` flag to point to the directory containing it).*

3. **Fuse the Model**:
Merge your medical adapter with the base model into a single new model.
```bash
python -m mlx_lm.fuse \
    --model Qwen/Qwen2.5-0.5B-Instruct \
    --adapter-path my_medical_adapter \
    --save-path my_fused_medical_model
```

---

## Step 3: Convert to GGUF
To run it on our highly optimized inference server, we need to convert it to GGUF format and quantize it to 4-bit (which saves memory and makes it run insanely fast on the M2).

If you are using MLX, you can convert it using `llama.cpp`'s conversion script:
```bash
# Clone the llama.cpp repository
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
pip install -r requirements.txt

# Convert to GGUF
python convert_hf_to_gguf.py ../my_fused_medical_model --outfile ../my_clinic_ai-q4_k_m.gguf --outtype q4_1
```
Now you have your custom brain: `my_clinic_ai-q4_k_m.gguf`!

---

## Step 4: Start the Private AI Server

Now we load your custom brain into the custom server so ElseaAI can chat with it.

1. **Install Server Dependencies with Apple Metal Support**:
This is the most critical step. You MUST install `llama-cpp-python` with Metal enabled so it utilizes the Mac M2 GPU.
```bash
CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python fastapi uvicorn
```

2. **Set the Model Path**:
Open `server.py` and change the `MODEL_PATH` to point to your new file:
```python
MODEL_PATH = os.environ.get("MODEL_PATH", "my_clinic_ai-q4_k_m.gguf")
```

3. **Run the Server**:
```bash
python server.py
```
Your server is now running on `http://localhost:8000`! You can connect to it securely from your frontend application.
