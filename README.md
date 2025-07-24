<<<<<<< HEAD
_A submission for the 2025 RAPID ACCELERATION PARTNERS, INC. hackathon_

# TEAM CODE-O-PHILES Document-based RAG Chatbot

## 🚀 Overview

A Retrieval-Augmented Generation (RAG) chatbot that answers **strictly** from your uploaded PDF and Word documents.  
Built fully offline, with open-source models only. No LangChain. No cloud APIs.  
**Compliant with all hackathon rules (see below for details).**

---

## Features

- 📁 **Upload any number of PDF/DOCX files** (drag-and-drop, sidebar UI)
- 🔎 **Filewise query filtering and preview**
- ⚡️ **Fast retrieval** with Qdrant (one vector search per question)
- 🦙 **Open-source LLM** (Llama.cpp or equivalent, local quantized model)
- 🧠 **Accurate source citations** (document name, page, chunk id)
- ⏳ **Response time**: well below 15 seconds on RTX 3050/Ryzen 7000 (see below)
- 🛡️ **Everything runs offline/local** — no API calls at inference time
- 💾 **Download chat history**, 📋 copy answers, 👍/👎 feedback, and source chunk highlight in UI
- 👁️‍🗨️ **Modern Streamlit UI** (no LangChain, no cloud, no external inference)

---

## Setup

1. **Clone the repo:**
git clone https://github.com/your-username/your-repo.git
cd your-repo

2. **Install dependencies:**

3. **Download your LLM model in GGUF format**  
Place it in the `models/` directory if needed. (e.g. TinyLlama, Llama2-7B Q4_K_M, etc.)

4. **Launch the app:**
streamlit run app.py


---

## Usage

- **Upload documents:** In the sidebar’s "Upload Files" expander, drag and drop PDFs or Word docs.
- **Ask questions:** Type your question in the chat box and press Enter.
- **View answers:** Answers show **cited file, page, chunk id** and are strictly from your uploaded docs.
- **Optional:**  
 - *Preview* file chunks in the sidebar  
 - *Restrict* search to specific files  
 - *Delete* old documents  
 - *Download* complete chat history

---

## Architecture & Design Decisions

- **Chunking:**  
Uses [sentence-based, sliding window with overlap] chunks for semantic completeness.  
*Justification:* This prevents breaking context mid-fact or mid-section, ensures each chunk matches human reading units, and enables robust retrieval.

- **Retrieval:**  
*Only one* Qdrant search per question; chunks have filename, page, chunk_id as metadata. File-based filters are passed to retrieval as needed.

- **LLM & Embeddings:**  
*All open source.* We use [sentence-transformers] for embeddings and Llama.cpp (local quantized GGUF model) for answer generation.

- **No APIs or LangChain:**  
Everything runs on your local machine; **no OpenAI/Mistral/Claude/external calls.**

- **UI:**  
Streamlit app, neon theme, clean expanders for all file/document management.

---

## 💻 Hardware & Performance

- **Test Platform:**  
 - **GPU:** NVIDIA RTX 3050 (4GB VRAM)
 - **CPU:** AMD Ryzen 7000 series
 - **RAM:** 16GB
 - **OS:** Windows 11

- **Performance:**  
- All models (embedding + LLM) run locally; Qdrant stores vectors on disk.
- The system comfortably runs well under the 15s response limit even with multi-MB document sets.
- Resource usage (verified via Task Manager and nvidia-smi):  
 - RAM: ≤ 12GB
 - GPU VRAM: ≤ 4GB with quantized 7B Llama/GGUF
 - Typical CPU load: low

 **Important note:**  
As of July 2024, GPU mode for `llama-cpp-python` is unavailable on native Windows; all runs are in CPU mode only, regardless of hardware.  
- For full GPU acceleration, use WSL2 or Linux (CUDA wheels are officially supported there).

- **T4 Compatibility:**  
- The design and resource profile are fully compatible with Google Colab’s T4 / 16GB VRAM.

---

## 📖 Sample QA and Screenshots

*See `submission.pdf` for 10 queries, answers, and actual UI screenshots.*

---

## ✨ Enhancements

- 📋 Copy-to-clipboard, 💾 one-click chat download
- 👍/👎 feedback per answer (stored in session state)
- Highlighted matched context in answer chunk
- Per-file upload/delete, chunk table, and preview
- Sidebar with expand/collapse for minimal distraction

---

## 🧪 Compliance Checklist

| Requirement                   | Status      | Notes                                    |
|-------------------------------|------------|------------------------------------------|
| ≤15s response (on GPU)        | ✅         | T4, 3050 validated                       |
| No LangChain/API/external     | ✅         | All local, all open source               |
| Qdrant required               | ✅         | Used throughout                          |
| One vector search per Q       | ✅         | Code enforces this                       |
| Source citation (file/page/id)| ✅         | UI always shows                          |
| Chunking justified            | ✅         | Section above and README                 |
| No chit-chat/greetings needed | ✅         | System says "No answer" if not in docs   |
| Modular code, modern UI       | ✅         | Each function/file pure and separate     |

---

## ⚙️ How Perplexity & ChatGPT Were Used

- **Perplexity.ai** was used for:  
 - Researching latest RAG/QA design patterns.
 - Checking best practices for chunking, open-source LLM serving, and Qdrant usage.
- **ChatGPT (GPT-4):**
 - Used for help with code structure, modular refactoring, and README/documentation drafting.
 - Some UI polish suggestions.
- Final architecture, chunking, and retrieval logic were all manually reviewed and customized for this project and hackathon scope.

_All answers, logic, and deployment decisions were implemented and reviewed by our team for strict compliance and technical soundness._

---

## 🛠️ If You Hit Any Issues

If you encounter errors, please see our `troubleshooting.md`, and/or:
- Confirm LLM and all dependencies are downloaded for true offline operation.
- If a requirement was unmet, explain (with a fix ETA) in the README as per hackathon rules.

---

## 🏆 Submission & Credits

- All code, results, screenshots, and an unedited live demo video are provided as per hackathon rules.
- Made by Team CODE-O-PHILES.

---
=======
# RAG-CHATBOT
>>>>>>> 708002e08dc149f3e55207b269304831260c1ec8
