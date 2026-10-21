import os
import tempfile

import streamlit as st
from markitdown import MarkItDown

SUPPORTED_TYPES = [
    "pdf", "docx", "pptx", "xlsx", "xls",
    "html", "htm", "csv", "json", "xml", "txt",
    "jpg", "jpeg", "png",
    "mp3", "wav",
    "zip", "epub",
]

st.set_page_config(page_title="MarkItDown Desktop GUI", page_icon="📝", layout="centered")


@st.cache_resource
def get_converter() -> MarkItDown:
    """Create the MarkItDown converter once and reuse it across reruns."""
    return MarkItDown()


def convert_file(uploaded_file) -> str:
    """Write the upload to a temp file, convert it, and always clean up."""
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    try:
        result = get_converter().convert(tmp_path)
        # Newer MarkItDown uses .markdown, older versions use .text_content
        text = getattr(result, "markdown", None) or getattr(result, "text_content", "")
        return text or ""
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


st.title("MarkItDown Desktop GUI")
st.write("Convert Office documents, PDFs, audio, and images into clean Markdown locally.")

uploaded_file = st.file_uploader("Choose a file to convert", type=SUPPORTED_TYPES)

# Forget the previous result when the user picks a different file or clears it.
current_id = uploaded_file.file_id if uploaded_file is not None else None
if st.session_state.get("file_id") != current_id:
    st.session_state.file_id = current_id
    st.session_state.markdown = None
    st.session_state.source_name = None

if uploaded_file is not None and st.button("Convert to Markdown", type="primary"):
    with st.spinner("Converting..."):
        try:
            st.session_state.markdown = convert_file(uploaded_file)
            st.session_state.source_name = uploaded_file.name
        except Exception as e:
            st.session_state.markdown = None
            st.error(f"Error during conversion: {e}")

# Results live in session_state so they survive the rerun that the
# download button triggers when clicked.
if st.session_state.get("markdown") is not None:
    markdown_text = st.session_state.markdown
    base_name = os.path.splitext(st.session_state.source_name)[0]

    if markdown_text.strip():
        st.success("Conversion successful!")
    else:
        st.warning("Conversion finished, but no text was extracted from this file.")

    st.text_area("Markdown Output", markdown_text, height=300)

    st.download_button(
        label="Download Markdown File",
        data=markdown_text,
        file_name=f"{base_name}.md",
        mime="text/markdown",
    )