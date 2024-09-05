import streamlit as st

def download_markdown(markdown_text):
    """
    Provide a download button for the markdown version of the resume.
    
    Args:
        markdown_text (str): The markdown text of the resume.
    """
    st.download_button("Download Markdown Resume", markdown_text, file_name="full_resume.md")

def download_docx(docx_buffer):
    """
    Provide a download button for the DOCX version of the resume.
    
    Args:
        docx_buffer (io.BytesIO): The DOCX file in bytes.
    """
    st.download_button(
        label="Download DOCX Resume",
        data=docx_buffer,
        file_name="full_resume.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
