import streamlit as st
from backend.pdf_utils import extract_text_from_pdf, chunk_text
from backend.rag_pipeline import RAGPipeline

st.title("Upload Telecom Document")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    with st.spinner("Processing document..."):
        text = extract_text_from_pdf(uploaded_file)
        chunks = chunk_text(text)

        if "rag" not in st.session_state:
            st.session_state.rag = RAGPipeline()

        st.session_state.rag.create_embeddings(chunks)

    st.success("Document processed successfully")

st.set_page_config(page_title="Document Upload", layout="wide")

st.markdown("""
<style>
.upload-box {
    background-color: #1e293b;
    padding: 40px;
    border-radius: 15px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.title("Upload Telecom Documents")

st.markdown("<div class='upload-box'>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Plan / Policy Document",
    type=["pdf", "txt", "docx"]
)

if uploaded_file:
    st.success("Document uploaded successfully.")
    st.write("Filename:", uploaded_file.name)

st.markdown("</div>", unsafe_allow_html=True)