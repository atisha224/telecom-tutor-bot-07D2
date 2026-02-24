import streamlit as st
import os
import sqlite3
from backend.rag_pipeline import RAGPipeline
from backend.pdf_utils import extract_text_from_pdf, chunk_text

if "role" not in st.session_state or st.session_state.role != "admin":
    st.warning("Admin access required")
    st.stop()
UPLOAD_FOLDER = "documents"
DB_NAME = "telequiz.db"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("🛠 Admin Panel")

# ==============================
# SIMPLE ADMIN AUTH
# ==============================
st.sidebar.title("Admin Login")

admin_user = st.sidebar.text_input("Admin Username")
admin_pass = st.sidebar.text_input("Admin Password", type="password")

if admin_user != "admin" or admin_pass != "admin123":
    st.warning("Admin login required.")
    st.stop()

st.success("Admin Authenticated")

# ==============================
# INIT RAG
# ==============================
if "admin_rag" not in st.session_state:
    st.session_state.admin_rag = RAGPipeline()

# ==============================
# DOCUMENT UPLOAD
# ==============================
st.subheader("📄 Upload Telecom Document")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"Document saved: {uploaded_file.name}")

    # Store metadata in DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        document_id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_name TEXT,
        upload_date TEXT
    )
    """)

    cursor.execute("""
    INSERT INTO documents (document_name, upload_date)
    VALUES (?, datetime('now'))
    """, (uploaded_file.name,))

    conn.commit()
    conn.close()

# ==============================
# REBUILD FAISS INDEX
# ==============================
st.subheader("🔁 Rebuild Knowledge Base")

if st.button("Rebuild FAISS Index from All Documents"):

    all_chunks = []

    for file in os.listdir(UPLOAD_FOLDER):
        if file.endswith(".pdf"):
            path = os.path.join(UPLOAD_FOLDER, file)
            with open(path, "rb") as f:
                text = extract_text_from_pdf(f)
                chunks = chunk_text(text)
                all_chunks.extend(chunks)

    if all_chunks:
        st.session_state.admin_rag.create_embeddings(all_chunks)
        st.success("FAISS index rebuilt successfully.")
    else:
        st.warning("No documents found.")

# ==============================
# VIEW UPLOADED DOCUMENTS
# ==============================
st.subheader("📂 Uploaded Documents")

conn = sqlite3.connect(DB_NAME)
docs = conn.execute("SELECT * FROM documents").fetchall()
conn.close()

if docs:
    for doc in docs:
        st.write(f"• {doc[1]} (Uploaded: {doc[2]})")
else:
    st.info("No documents uploaded yet.")