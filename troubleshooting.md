# Troubleshooting Guide: CODE-O-PHILES RAG Chatbot

## 1. Streamlit App won't start / "No module named ..." error
- **Fix**: Run `pip install -r requirements.txt` (from your project root folder).
- **Note**: You need Python 3.8+ for all dependencies.

## 2. "Could not load model" or "GGUF not found"
- **Fix**: 
    - Download your LLM GGUF file (example: TinyLlama or Llama2) and place it in your `models/` directory.
    - Edit `config.py` or `answer_question.py` if you used a non-standard filename.

## 3. "Qdrant not found" or vector DB errors
- **Fix**: 
    - Make sure `qdrant-client` is installed (`pip install qdrant-client`).
    - Ensure permissions for local `qdrant_data/` or your vector storage directory.

## 4. Errors related to chunking: "No chunks generated", "ERR" in chunk table, etc.
- **Fix**: 
    - Check your PDF/DOCX is valid and not password-protected or encrypted.
    - Try re-saving the file in a PDF Editor or Word, and re-uploading.
    - If you see only "ERR", ensure you have `python-docx`, `pymupdf`, and `nltk` installed.

## 5. Out of Memory (RAM or GPU), slow answers
- **Fix**: 
    - Make sure to use a quantized (small) GGUF model, such as TinyLlama or Llama 7B Q4_K_M.
    - Reduce the number of uploaded files or use smaller PDFs.
    - Restart your machine to free up resources.

## 6. UI: Sidebar doesn't respond, options missing, or theme broken
- **Fix**: 
    - Refresh the Streamlit page in your browser (F5).
    - If running behind a proxy or on Windows, try `streamlit run app.py --server.headless true`.

## 7. "AttributeError: answer_question got unexpected keyword ..." 
- **Fix**: 
    - Upgrade your backend scripts for `answer_question()` to support `file_filters` argument if you want file-wise filtering.
    - Or, use a version that ignores the extra argument safely.

## 8. Cannot run completely offline (unexpected downloads)
- **Fix**: 
    - Download all models and embeddings **before** disconnecting from the internet.
    - Run a dummy session while online before your livestream demo so HuggingFace etc. cache all weights.

## 9. Feature Not Working / New Error
- **Try**:
    - Re-run install, check for missing packages.
    - Review the latest commits in the project's GitHub issues or this file.
    - Contact the maintainers (via [your team emails or GitHub]).

---

## [If we failed to meet a requirement:]
- We were unable to complete ___.  
  **ETA to fix:** X days/hours.  
  **Next steps:** ___

---

**Tips:**
- If no answer is returned, check the document chunking–sometimes the relevant answer is split or missing.

Good luck and thank you for testing our chatbot!
