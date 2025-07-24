#app.py
import streamlit as st
import os
import re
import time
import pandas as pd
from answer_question import answer_question
from data_loader import load_documents_from_folder
from embedder import embed_and_store_chunks
from qdrant_helper import create_collection as create_or_load_index
from chunker import process_documents

# == NEON TECH THEME CSS ==
st.set_page_config(page_title="TEAM CODE-O-PHILES RAG Chatbot", layout="wide")
st.markdown("""
    <style>
        body { background: #101926; color: #F2F6FF;}
        .stApp { background: #101926; }
        h1, h2, .stTitle { color: #26f7fd !important; text-shadow: 0 0 7px #26f7fd99, 0 0 2px #26f7fd33; font-family: 'Orbitron', sans-serif; letter-spacing: 1px;}
        section[data-testid="stSidebar"] { background: #181e28 !important; border-right:2px solid #26f7fd2a;}
        .st-bb { background: #26f7fd !important; color: #07354b !important;}
        .stButton > button, .stDownloadButton > button { background: #181e28; color: #26f7fd; border: 1px solid #26f7fd; border-radius: 7px; font-weight: bold; box-shadow: 0 0 8px #26f7fd33;}
        .stButton > button:hover, .stDownloadButton > button:hover { background: #0d282e; color: #20fcc4; border-color: #59d1eb;}
        .stInfo { background: #182955 !important; color: #76E1FF !important; font-size:1.04rem; border-left: 4px solid #26f7fd;}
        .stExpanderHeader { color: #26f7fd !important; font-weight: 700; text-shadow: 0 0 6px #08F7FE44, 0 0 1px #fff;}
        .stExpander { background: #152032 !important; border-radius: 10px !important; color: #76E1FF;}
        .user-bubble {
            background: linear-gradient(90deg,#18395b 30%,#102b2c 90%); color: #26f7fd;
            border-radius: 14px; margin-bottom: 1rem; padding: 14px 22px 12px 18px; border:2px solid #26f7fd66;
            font-weight:500; font-size:1.07rem; line-height:1.575;
            word-break:break-word; font-family: 'Inter','Segoe UI',sans-serif;
        }
        .bot-bubble {
            background: linear-gradient(93deg, #0c1b26 70%, #001c37 100%);
            color:#fff !important; border-radius:14px; margin-bottom:1.05rem; padding:13px 20px 15px 19px;
            border:2px solid #26f7fd; font-size:1.07rem; font-weight:500; line-height:1.6; box-shadow: 0 0 7px #1ad7ea36;
            word-break:break-word; font-family: 'Inter','Segoe UI',sans-serif;
        }
        .chat-meta-divider {border-bottom:1.2px solid #18b7ea22; margin:1.5rem 0 .3rem 0;}
        .stMarkdown, .stTextInput, .stTextArea { color: #e7fbff; font-size: 1.08rem;}
        .scroll-box-chat {
            max-height: 470px;
            min-height: 240px;
            overflow-y: auto;
            padding: 18px;
            background: #101926;
            border-radius: 18px;
            margin-bottom: 18px;
            border: 2px solid #26f7fd22;
            box-shadow: 0 0 17px #19e0ff22;
            scrollbar-width: thin;
            scrollbar-color: #26f7fd #152032;
        }
        .scroll-box-chat::-webkit-scrollbar {
            width: 8px;
            background: #152032;
        }
        .scroll-box-chat::-webkit-scrollbar-thumb {
            background: #26f7fd;
            border-radius: 8px;
        }
    </style>
    <link href="https://fonts.googleapis.com/css?family=Orbitron:700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

st.title("🤖 TEAM CODE-O-PHILES RAG Chatbot")

docs_dir = "documents"
os.makedirs(docs_dir, exist_ok=True)
st.info(
    "❗️ This chatbot does not handle greetings or open conversation. All answers come strictly from the uploaded documents."
)

with st.sidebar:
    st.markdown(
        "<div style='text-align:center; font-size:1.7em; margin-bottom:-1em;'>☰</div>",
        unsafe_allow_html=True)

    # --- Upload
    with st.expander("📂 Upload Files", expanded=False):
        uploaded_files = st.file_uploader(
            "Upload PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True
        )
        if uploaded_files:
            saved_paths = []
            new_upload = False
            for file in uploaded_files:
                file_path = os.path.join(docs_dir, file.name)
                if (not os.path.exists(file_path)) or (file.getbuffer().nbytes != os.path.getsize(file_path)):
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    saved_paths.append(file_path)
                    new_upload = True
            if new_upload:
                with st.spinner("Processing and ingesting uploaded documents..."):
                    chunks = load_documents_from_folder(docs_dir)
                    chunk_count = len(chunks)
                    if chunk_count == 0:
                        st.error("No chunks generated. Please check your files.", icon='🚫')
                    else:
                        st.success(f"✅ {len(saved_paths)} file(s) ingested! {chunk_count} chunks total.")
                        embed_and_store_chunks(chunks)
            else:
                st.info("No new files uploaded or all files up-to-date.")

    # --- Delete
    with st.expander("🗑️ Delete/Manage Uploaded Files", expanded=False):
        existing_files = [f for f in os.listdir(docs_dir) if f.lower().endswith(('.pdf', '.docx'))]
        to_del = st.multiselect("Select file(s) to delete:", options=existing_files, key="delete_sidebar")
        if st.button("Delete Selected"):
            for fname in to_del:
                try:
                    os.remove(os.path.join(docs_dir, fname))
                    st.success(f"Deleted: {fname}", icon="✅")
                except Exception as e:
                    st.error(f"Problem deleting {fname}: {e}")
            st.experimental_rerun()

    # --- Chunk Table & Preview
    with st.expander("📊 Chunk Status + Preview", expanded=False):
        def chunk_preview_and_table():
            docs = [f for f in os.listdir(docs_dir) if f.endswith(('.pdf', '.docx'))]
            file_counts, preview_chunks = [], {}
            for f in docs:
                path = os.path.join(docs_dir, f)
                try:
                    chunks = process_documents([path])
                    file_counts.append({"Document": f, "Chunks": len(chunks)})
                    preview_chunks[f] = chunks[0]["chunk_text"][:350] + ("..." if len(chunks[0]["chunk_text"]) > 350 else "")
                except Exception:
                    file_counts.append({"Document": f, "Chunks": "ERR"})
                    preview_chunks[f] = "Preview failed."
            return file_counts, preview_chunks
        file_counts, preview_chunks = chunk_preview_and_table()
        if file_counts:
            st.write("**Chunk Table:**")
            st.dataframe(pd.DataFrame(file_counts), use_container_width=True)
            doc_to_preview = st.selectbox("Preview doc:", list(preview_chunks.keys()), key="doc_prev")
            st.code(preview_chunks[doc_to_preview], language="markdown")

    # --- File-wise Filtering
    with st.expander("🔎 File-wise Query Filter", expanded=False):
        existing_files = [f for f in os.listdir(docs_dir) if f.lower().endswith(('.pdf', '.docx'))]
        filter_files = st.multiselect(
            "Restrict Query to Files (optional)", options=existing_files, key="file_filter"
        )

try:
    create_or_load_index()
except Exception as e:
    st.error(f"Failed to load Qdrant collection: {e}")

st.markdown("---")
st.subheader("💬 Ask about your uploaded documents:")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "<span style='color:#26f7fd'>👋 Hello! Ask me anything about your uploaded documents.</span>"}
    ]
if "feedback" not in st.session_state:
    st.session_state.feedback = []

def render_source(source, highlight=None):
    if source:
        with st.expander("📄 Source Context", expanded=False):
            st.text(f"📁 File: {source.get('filename', 'N/A')}")
            st.text(f"📄 Page: {source.get('page_number', 'N/A')} | 🔖 Chunk ID: {source.get('chunk_id', 'N/A')}")
            st.markdown("#### 📌 Matched Text")
            matched = source.get("chunk_text", "")
            if highlight and highlight in matched:
                pat = re.escape(highlight.strip())
                matched = re.sub(f'({pat})', r'<mark style="background: #26f7fd44">\1</mark>', matched, flags=re.I)
                st.markdown(f"<div style='color:#eee'>{matched}</div>", unsafe_allow_html=True)
            else:
                st.info(matched)
    else:
        st.info("No matching document chunk found.")

def pretty_bot_answer(ans):
    ans = ans.strip()
    ans = re.sub(r'(\d+\.)', r'\n\1', ans)
    lines = [l.strip() for l in ans.split('\n') if l.strip()]
    bullet_pat = re.compile(r'^(\d+\.|-|\u2022|\*)\s*')
    found_bullet = any(bullet_pat.match(l) for l in lines)
    if found_bullet:
        bullet_strs = []
        for l in lines:
            s = bullet_pat.sub('', l)
            if re.match(r'^\d+\.', l):
                bullet_strs.append(f'{l}')
            else:
                bullet_strs.append(f'- {s}')
        return "\n".join(bullet_strs)
    if len(lines) > 2 and not found_bullet:
        return "\n".join(f"- {l}" for l in lines)
    return ans

user_input = st.chat_input("Type your question here and hit Enter...", key="chat_input")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.spinner("Thinking..."):
        t0 = time.time()
        files_to_filter_on = filter_files if filter_files else None
        result = answer_question(user_input, file_filters=files_to_filter_on) if 'file_filters' in answer_question.__code__.co_varnames else answer_question(user_input)
        elapsed = time.time() - t0

        answer = result.get("answer", "No answer generated.")
        source = result.get("source")
        answer_msg = pretty_bot_answer(answer)
        highlight_snippet = answer if source and answer and answer.lower() in source.get("chunk_text", "").lower() else None

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer_msg + f"\n\n<span style='font-size:.82em;color:#7ee1fe;'>⏱️ Response time: {elapsed:.2f} sec</span>",
            "source": source,
            "highlight": highlight_snippet
        })
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "<span style='color:#26f7fd'>🤖 Do you have another question about your documents?</span>"
        })

with st.container():
    st.markdown('<div class="scroll-box-chat" id="chat-scrollbox">', unsafe_allow_html=True)
    for idx, msg in enumerate(st.session_state.chat_history):
        role = msg["role"]
        if role == "user":
            st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
        elif role == "assistant":
            is_main_answer = ("source" in msg and msg["source"])
            copy_button_html = (
                ' <br><button onclick="navigator.clipboard.writeText(this.previousSibling.textContent);" '
                'style="background:#182955;color:#80f7fd;border:1.3px solid #2ef1fd;border-radius:7px;'
                'font-size:14px;padding:2px 8px;margin-left:16px;">📋 Copy</button>'
                if is_main_answer else ''
            )
            bubble = f"<div class='bot-bubble'>{msg['content']}{copy_button_html}</div>"
            st.markdown(bubble, unsafe_allow_html=True)
            if "source" in msg and msg["source"]:
                render_source(msg["source"], highlight=msg.get("highlight"))
                # Feedback buttons
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("👍", key=f"fbup_{idx}"):
                        st.session_state.feedback.append({"index": idx, "sentiment": "up"})
                        st.success("Thanks for your feedback!")
                with col2:
                    if st.button("👎", key=f"fbdn_{idx}"):
                        st.session_state.feedback.append({"index": idx, "sentiment": "down"})
                        st.info("We'll use your feedback to improve.")
        if idx < len(st.session_state.chat_history) - 1:
            st.markdown("<div class='chat-meta-divider'></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Download chat history
history_lines = [
    f"{msg['role'].capitalize()}: {re.sub('<.*?>','',msg['content'])}"
    for msg in st.session_state.chat_history
]
history_text = "\n\n".join(history_lines)
st.download_button("💾 Download Chat History", history_text, "chat_history.txt", "text/plain")

# Scroll-to-bottom
st.markdown("""
<script>
  var chatScrollBox = document.getElementById('chat-scrollbox');
  if(chatScrollBox){ chatScrollBox.scrollTop = chatScrollBox.scrollHeight; }
</script>
""", unsafe_allow_html=True)
