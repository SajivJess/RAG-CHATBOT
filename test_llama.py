from llama_cpp import Llama
llm = Llama(model_path="models/llama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf", n_gpu_layers=-1)
print("Model loaded.")
output = llm("What is AI?", max_tokens=32)
print(output)
