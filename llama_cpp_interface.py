from llama_cpp import Llama
llm = Llama(model_path="models/llama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf", n_gpu_layers=-1)
# -1 = put all layers on GPU; you can set a partial number, e.g., 10, based on your VRAM
from config import LLM_MODEL_PATH, LLM_MAX_INPUT_TOKENS, PROMPT_TEMPLATE, DEVICE
import os
import re

print(f"🦙 Loading GGUF model via llama.cpp ({DEVICE.upper()} mode)...")
llm = Llama(
    model_path=LLM_MODEL_PATH,
    n_ctx=LLM_MAX_INPUT_TOKENS,
    n_threads=os.cpu_count() or 4,
    n_gpu_layers=40 if DEVICE == "gpu" else 0,
    use_gpu=(DEVICE == "gpu"),
    verbose=False
)

def clean_repetitions(text: str) -> str:
    """
    Removes excessive sentence repetitions and normalizes whitespace.
    """
    sentences = re.split(r'(?<=[.?!])\s+', text.strip())
    seen = set()
    cleaned = []
    for sentence in sentences:
        s = sentence.strip()
        if s.lower() not in seen:
            cleaned.append(s)
            seen.add(s.lower())
    return " ".join(cleaned)

def generate_answer(chunk: dict, user_query: str) -> str:
    """
    Formats the prompt using the matched chunk and user's question,
    then generates an answer using LLaMA.
    """
    try:
        prompt = PROMPT_TEMPLATE.format(
            filename=chunk.get("filename", ""),
            page_number=chunk.get("page_number", ""),
            chunk_id=chunk.get("chunk_id", ""),
            chunk_text=chunk.get("chunk_text", ""),
            user_query=user_query
        )

        print("🧠 Generating answer...")
        result = llm(
            prompt,
            max_tokens=256,
            temperature=0.2,
            stop=["\n\n", "User:", "###"],
            echo=False
        )

        raw_answer = (
            result["choices"][0]["text"].strip()
            if isinstance(result["choices"][0], dict)
            else result["choices"][0].strip()
        )
        return clean_repetitions(raw_answer)

    except Exception as e:
        print(f"❌ LLM generation failed: {e}")
        return "Failed to generate an answer."
