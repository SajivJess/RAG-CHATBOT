# 🤖 TEAM CODE-O-PHILES — Document-based RAG Chatbot

---

## 🚀 Overview
A **Retrieval-Augmented Generation (RAG) chatbot** that answers **strictly** from your uploaded PDF and Word documents.  
Built fully **offline**, using **open-source models only** — **No LangChain. No cloud APIs.**

✅ **Compliant with all hackathon rules** (see compliance checklist below).

---

## ✨ Features
- 📁 Upload any number of PDF/DOCX files (drag-and-drop, sidebar UI)
- 🔎 Filewise query filtering and preview
- ⚡ Fast retrieval with Qdrant (**one vector search per question**)
- 🦙 Open-source LLM (Llama.cpp or equivalent, local quantized model)
- 🧠 Accurate source citations (document name, page, chunk ID)
- ⏳ Response time: <15 seconds on RTX 3050 / Ryzen 7000
- 🛡️ 100% Offline — no API calls at inference time
- 💾 Download chat history, 📋 copy answers, 👍/👎 feedback
- 📄 Source chunk highlighting in UI
- 👁️‍🗨️ Modern Streamlit UI (no LangChain, no cloud, no external inference)

---

## 🎥 Demo Video
📌 [**Watch Demo**](https://drive.google.com/drive/folders/1wRsFsptnuP_xbp1jgTxkt3wvQEe83iXU?usp=sharing)

---

## ⚙️ Setup

### 1️⃣ Clone the repo
```bash
git clone https://github.com/SajivJess/RAG-CHATBOT
cd RAG-CHATBOT
```

### 2️⃣ Install dependencies
Make sure **Python 3.10+** is installed, then run:
```bash
pip install -r requirements.txt
```

### 3️⃣ Download your LLM model (GGUF format)
Place it in the `models/` directory.

Examples:
- **TinyLlama**
- **Llama2-7B Q4_K_M**

### 4️⃣ Launch the app
```bash
streamlit run app.py
```

---

## 🛠️ Usage

1. 📥 **Upload documents** — Drag & drop PDFs or Word docs in the sidebar's "Upload Files" section.  
2. ❓ **Ask questions** — Type your query in the chat box and press Enter.  
3. 📄 **View answers** — Responses come strictly from uploaded docs, with cited file, page, and chunk ID.

### Optional Tools:
- 🔍 Preview file chunks in the sidebar
- 📂 Restrict search to specific files
- 🗑 Delete old documents
- 💾 Download complete chat history

---

## 🏗 Architecture & Design Decisions

### 📄 Chunking
- **Sentence-based**, sliding window with overlap for semantic completeness
- Prevents breaking context mid-fact
- Ensures natural reading units & improves retrieval quality

### 🔎 Retrieval
- **Single Qdrant vector search** per question
- Metadata includes `filename`, `page`, `chunk_id`
- File filters applied when needed

### 🦙 LLM & Embeddings
- **100% open-source**
- Embeddings: [`sentence-transformers`](https://www.sbert.net/)
- LLM: [`llama.cpp`](https://github.com/ggerganov/llama.cpp) (quantized GGUF model)

### 🎨 UI
- Built with **Streamlit**
- Neon theme
- Clean expanders for file/document management

---

## 💻 Hardware & Performance

**Test Platform:**
- 💻 GPU: NVIDIA RTX 3050 (4GB VRAM)
- ⚙️ CPU: AMD Ryzen 7000 series
- 🧠 RAM: 16GB
- 🖥 OS: Windows 11

**Performance:**
- All models run locally
- Qdrant stores vectors on disk
- Responses well under 15s even for large documents
- RAM ≤ 12GB
- GPU VRAM ≤ 4GB (quantized 7B Llama/GGUF)
- Low CPU load

> **Note:** GPU mode for `llama-cpp-python` is unavailable on native Windows (as of July 2024). Runs in CPU mode only. For GPU acceleration, use WSL2 or Linux.

---

## 📸 Sample QA & Screenshots
See **submission.pdf** for:
- 10 queries & answers
- Actual UI screenshots

---

## 🔧 Enhancements
- 📋 Copy-to-clipboard answers
- 💾 One-click chat download
- 👍/👎 Feedback per answer (stored in session state)
- 🔍 Highlight matched context in answer chunk
- 🗂 Per-file upload/delete
- 🖼 Sidebar expand/collapse for minimal distraction

---

## ✅ Compliance Checklist

| Requirement                       | Status | Notes |
|-----------------------------------|--------|-------|
| ≤15s response (on GPU)            | ✅     | Tested on T4 & RTX 3050 |
| No LangChain/API/external         | ✅     | Fully local |
| Qdrant required                   | ✅     | Implemented |
| One vector search per Q           | ✅     | Enforced |
| Source citation                   | ✅     | File/page/id in UI |
| Chunking justified                | ✅     | Sentence-based with overlap |
| No chit-chat                      | ✅     | Returns "No answer" if outside docs |
| Modular code, modern UI           | ✅     | Functionally separated |

---

## 🧪 How Perplexity & ChatGPT Were Used

**Perplexity.ai**
- Researched latest RAG/QA design patterns
- Studied chunking strategies
- Investigated open-source LLM serving & Qdrant usage

**ChatGPT (GPT-4)**
- Assisted in code structure & modular refactoring
- Helped polish README/documentation

> Final architecture, chunking, and retrieval logic were fully reviewed and implemented by the team for hackathon compliance.

---

## 🆘 Troubleshooting
If you encounter issues:
- Verify model & dependencies are downloaded for offline operation
- Check `troubleshooting.md` for fixes

---

## 🏆 Submission & Credits
All code, results, screenshots, and unedited live demo video provided as per hackathon rules.

👨‍💻 **Made by Team CODE-O-PHILES**
