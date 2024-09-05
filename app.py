import streamlit as st
import io
from modules.api_key_utils import get_google_api_key
from modules.pdf_utils import extract_pdf_text, clean_extracted_text
from modules.vectorstore_utils import create_vector_store, split_text
from modules.llm_pipeline import setup_rag_pipeline
from modules.resume_parser import process_resume, process_full_resume
from modules.markdown_to_docx import convert_markdown_to_docx  # Import the markdown-to-docx conversion function
from st_copy_to_clipboard import st_copy_to_clipboard  # For copying the resume text

def save_markdown_to_file(markdown_text, file_path):
    """
    Save markdown text to a file.
    
    Args:
        markdown_text (str): The markdown text to save.
        file_path (str): The file path to save the markdown.
    """
    with open(file_path, 'w') as f:
        f.write(markdown_text)

def main():
    st.title("Resume Rewriter Using Harvard Guidelines")

    # Get the API key
    google_api_key = get_google_api_key()

    if google_api_key:
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")

        if uploaded_file:
            if "resume_text" not in st.session_state:
                with st.spinner("Extracting text from PDF..."):
                    resume_text = extract_pdf_text(uploaded_file)
                    resume_text = clean_extracted_text(resume_text)
                    st.session_state.resume_text = resume_text
                    st.success("Resume text extracted!")

            # Display the original resume
            st.write("### Original Resume:")
            st.text_area("Resume Text", st.session_state.resume_text, height=300)

            if st.button("Rewrite Resume"):
                # Load Harvard Resume Guide
                with open("assets/harvard_resume_guide.md", "r") as file:
                    guide_text = file.read()

                # Create vector store
                chunks = split_text(guide_text)
                vector_store = create_vector_store(chunks)

                # Unpack the feedback and full resume rewrite chains
                feedback_chain, rewrite_chain, full_rewrite_chain = setup_rag_pipeline(vector_store)

                # Process the resume to get feedback and the rewritten version
                feedback, _ = process_resume(st.session_state.resume_text, feedback_chain, rewrite_chain, vector_store)
                full_resume = process_full_resume(feedback, st.session_state.resume_text, full_rewrite_chain)

                # Store feedback and full_resume in session state
                st.session_state.feedback = feedback
                st.session_state.full_resume = full_resume

            # If feedback and full_resume are available, display them
            if "feedback" in st.session_state and "full_resume" in st.session_state:
                st.markdown("### Feedback for Your Resume")
                feedback_text = "\n\n".join([f"**{section}**:\n{content}" for section, content in st.session_state.feedback.items()])
                st.markdown(feedback_text)

                # Display the full rewritten resume in Markdown
                st.markdown("### Full Rewritten Resume (Markdown format)")
                st.markdown(st.session_state.full_resume)

                # Render the "Copy Resume" button to copy raw markdown text to the clipboard
                st_copy_to_clipboard(st.session_state.full_resume, "Copy Resume to Clipboard")

                # Save the Markdown to a file when the user requests download
                markdown_file_path = "full_resume.md"
                save_markdown_to_file(st.session_state.full_resume, markdown_file_path)

                # Option to download the markdown file as well
                st.download_button("Download Markdown Resume (Recommended)", st.session_state.full_resume, file_name="full_resume.md")

                # When the user requests the DOCX download, convert the markdown to DOCX and provide the download
                if st.button("Download DOCX Resume"):
                    # Create a BytesIO buffer to hold the DOCX content
                    docx_buffer = io.BytesIO()
                    
                    # Copy the markdown text to anoother variable
                    markdown_text_tm = st.session_state.full_resume

                    # Convert the markdown to DOCX and save it to the buffer
                    convert_markdown_to_docx(markdown_text_tm, "full_resume.docx")
                    
                    # Read the saved DOCX file into the buffer
                    with open("full_resume.docx", "rb") as f:
                        docx_buffer.write(f.read())
                    
                    # Set the buffer position to the beginning
                    docx_buffer.seek(0)

                    # Provide the DOCX file for download
                    st.download_button(
                        label="Download DOCX Resume",
                        data=docx_buffer,
                        file_name="full_resume.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

    else:
        st.error("Google API key is required. Please provide the key in '.env' or Streamlit Secrets.")

if __name__ == "__main__":
    main()
