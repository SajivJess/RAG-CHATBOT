# data_loader.py

import os
from chunker import process_documents

def load_documents_from_folder(folder_path):
    document_paths = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".pdf", ".docx")):
            full_path = os.path.join(folder_path, filename)
            document_paths.append(full_path)

    if not document_paths:
        print("⚠️ No valid PDF or DOCX files found in folder:", folder_path)
        return []

    chunks = process_documents(document_paths)
    return chunks
