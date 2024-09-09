import streamlit as st
import io
from modules.api_key_utils import get_google_api_key
from modules.pdf_utils import extract_pdf_text, clean_extracted_text
from modules.vectorstore_utils import create_vector_store, split_text
from modules.llm_pipeline import setup_rag_pipeline
from modules.resume_parser import process_resume, process_full_resume
from modules.markdown_to_docx import convert_markdown_to_docx
from st_copy_to_clipboard import st_copy_to_clipboard  # For copying the resume text
from modules.ui_components import display_original_resume, display_feedback, display_rewritten_resume

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
    
    st.set_page_config(
        page_title="✨AI Resume Rewriter",
        page_icon="📝",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://careerservices.fas.harvard.edu/resources/bullet-point-resume-template/',  # Updated to a more relevant link
            'Report a bug': "https://github.com/Pouyaexe/AI-Resume/issues",  # GitHub Issues page for bug reporting
            'About': "## AI Resume Rewriter\n"
                    "This app uses Harvard Resume guidelines to improve and rewrite your resume. "
                    "Upload your resume and receive personalized feedback and suggestions."
                    "Contact the developer: [Pouya](https://pouyaexe.github.io/)"
                    "LinkedIn: [Pouya](https://www.linkedin.com/in/pouya-hallaj-zavareh/)"
        }
    )

    st.title("✨AI Resume Rewriter✨")
    st.subheader("Using Harvard Resume Guidelines to Rewrite Your Resume")
    
    # Introduction with explanation of the Harvard Resume Guide
    st.write("""
        Welcome to the AI Resume Rewriter powered by Harvard Guidelines.  
        This tool helps you transform your resume by offering detailed feedback and rewriting suggestions based on professional guidelines.
        Upload your resume in PDF format and let the AI assist you in polishing your resume to perfection!
    """)
    
    st.subheader("Why the Harvard Resume Guide?")
    st.write("""
        The **Harvard Resume Guide** is a highly regarded resource in professional resume writing. 
        It emphasizes the importance of clear formatting, strong action verbs, quantifiable achievements, and tailoring resumes for specific roles. 
        By following this guide, you ensure that your resume is aligned with industry standards and stands out to potential employers.
        
        This app analyzes your resume based on these best practices, offering personalized feedback and rewriting sections to meet the Harvard standard.
    """)
    
    st.write("🔗 [Learn more about the Harvard Resume Guide](https://hwpi.harvard.edu/files/ocs/files/undergrad_resume_hg.pdf)")

    # Divider line
    st.write("---")

    # Get the API key
    google_api_key = get_google_api_key()

    if google_api_key:
        uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type="pdf", help="Upload your resume in PDF format to start.")
        st.write("Upload your resume in PDF format, and the AI will process it to provide feedback and make improvements.")


        if uploaded_file:
            # Extract and display the original resume
            if "resume_text" not in st.session_state:
                with st.spinner("Extracting text from PDF..."):
                    resume_text = extract_pdf_text(uploaded_file)
                    resume_text = clean_extracted_text(resume_text)
                    st.session_state.resume_text = resume_text
                    st.success("✅ Resume text extracted!")

            display_original_resume(st.session_state.resume_text)

            # Add a button to rewrite the resume
            if st.button("Rewrite Resume ✍️"):
                with st.spinner("Generating feedback and rewriting your resume..."):
                    # Load Harvard Resume Guide
                    with open("assets/harvard_resume_guide.md", "r") as file:
                        guide_text = file.read()

                    # Create vector store
                    chunks = split_text(guide_text)
                    vector_store = create_vector_store(chunks)

                    # Set up pipelines
                    feedback_chain, rewrite_chain, full_rewrite_chain = setup_rag_pipeline(vector_store)

                    # Process the resume for feedback and full resume
                    feedback, _ = process_resume(st.session_state.resume_text, feedback_chain, rewrite_chain, vector_store)
                    full_resume = process_full_resume(feedback, st.session_state.resume_text, full_rewrite_chain)

                    # Store feedback and full resume in session state
                    st.session_state.feedback = feedback
                    st.session_state.full_resume = full_resume

            # Display results if available
            if "feedback" in st.session_state and "full_resume" in st.session_state:
                # Display feedback for the resume
                display_feedback(st.session_state.feedback)

                # Display the full rewritten resume in Markdown format
                display_rewritten_resume(st.session_state.full_resume)

                # Create a row with three buttons: Copy, Download Markdown, and Download DOCX
                col1, col2, col3 = st.columns(3)

                with col1:
                    # Copy Resume button
                    st_copy_to_clipboard(st.session_state.full_resume, "📋 Copy Resume to Clipboard")

                with col2:
                    # Download Markdown button
                    st.download_button("💾 Download Markdown Resume", st.session_state.full_resume, file_name="full_resume.md")

                with col3:
                    # Download DOCX button (handled within the same column)
                    docx_buffer = io.BytesIO()
                    convert_markdown_to_docx(st.session_state.full_resume, "full_resume.docx")
                    
                    with open("full_resume.docx", "rb") as f:
                        docx_buffer.write(f.read())
                    
                    docx_buffer.seek(0)

                    st.download_button(
                        label="💾 Download DOCX Resume",
                        data=docx_buffer,
                        file_name="full_resume.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

    else:
        st.error("Google API key is required. Please provide the key in '.env' or Streamlit Secrets.")

if __name__ == "__main__":
    main()
