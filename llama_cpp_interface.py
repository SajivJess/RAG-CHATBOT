import os
import re
from config import LLM_MODEL_PATH, LLM_MAX_INPUT_TOKENS, PROMPT_TEMPLATE, DEVICE
from llama_cpp import Llama

# Set model context window: TinyLlama Q4_K_M supports 1024 tokens; limit accordingly.
N_CTX = min(LLM_MAX_INPUT_TOKENS, 1024)
N_GPU_LAYERS = 40 if DEVICE.lower() == "gpu" else 0

print(f"🦙 Loading GGUF model via llama.cpp ({DEVICE.upper()} mode)...")
llm = Llama(
    model_path=LLM_MODEL_PATH,
    n_ctx=N_CTX,
    n_threads=os.cpu_count() or 4,
    n_gpu_layers=N_GPU_LAYERS,
    use_gpu=(DEVICE.lower() == "gpu"),
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
        if s and s.lower() not in seen:
            cleaned.append(s)
            seen.add(s.lower())
    return " ".join(cleaned)

def generate_answer(chunk: dict, user_query: str) -> str:
    """
    Formats the prompt using the matched chunk and user's question,
    then generates an answer using LLaMA.
    """
    try:
        # Truncate chunk_text to ~2000 chars (~512 tokens conservatively)
        chunk_text = chunk.get("chunk_text", "")[:2000]

        prompt = PROMPT_TEMPLATE.format(
            filename=chunk.get("filename", ""),
            page_number=chunk.get("page_number", ""),
            chunk_id=chunk.get("chunk_id", ""),
            chunk_text=chunk_text,
            user_query=user_query
        )

        print("🧠 Generating answer...")
        result = llm(
            prompt,
            max_tokens=128,  # Stay well under 1024 context tokens
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

