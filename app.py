import os
import streamlit as st
from dotenv import load_dotenv  # Import the dotenv package
from modules.pdf_utils import extract_pdf_text, clean_extracted_text
from modules.vectorstore_utils import create_vector_store, split_text
from modules.llm_pipeline import setup_rag_pipeline
from modules.resume_parser import process_resume

# Function to get the Google API key from Streamlit secrets (Cloud and Local)
def get_google_api_key():
    """Get the Google API key from Streamlit secrets."""
    try:
        # Attempt to get the API key from Streamlit secrets (used in Cloud and locally via secrets.toml)
        api_key = st.secrets["GOOGLE_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = api_key  # Set it in the environment for later use
        return api_key
    except KeyError:
        st.error("API key not found. Please ensure that 'secrets.toml' contains the key locally or it is provided in Streamlit Cloud secrets.")
        return None


def main():
    st.title("Resume Rewriter Using Harvard Guidelines")

    # Get the API key from secrets or .env
    google_api_key = get_google_api_key()

    if google_api_key:
        # Proceed if API key is available
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
        
        if uploaded_file:
            with st.spinner("Extracting text from PDF..."):
                resume_text = extract_pdf_text(uploaded_file)
                resume_text = clean_extracted_text(resume_text)
                st.success("Resume text extracted!")

            st.write("### Original Resume:")
            st.text_area("Resume Text", resume_text, height=300)

            if st.button("Rewrite Resume"):
                # Load Harvard Resume Guide
                with open("assets/harvard_resume_guide.md", "r") as file:
                    guide_text = file.read()

                # Split guide into chunks and create vector store
                chunks = split_text(guide_text)
                vector_store = create_vector_store(chunks)

                # Unpack the feedback and rewrite chains
                feedback_chain, rewrite_chain = setup_rag_pipeline(vector_store)

                # Process the resume to get feedback and the final rewritten resume
                feedback, improved_resume = process_resume(resume_text, feedback_chain, rewrite_chain, vector_store)

                # Display feedback first
                st.markdown("### Feedback for Your Resume")
                feedback_text = "\n\n".join([f"{section}:\n{content}" for section, content in feedback.items()])
                st.markdown(feedback_text)

                # Display the final full rewritten resume
                st.markdown("### Full Rewritten Resume (Markdown format)")

                # Combine section titles and their content
                improved_resume_text = "\n\n".join([f"###{content}" for section, content in improved_resume.items()])

                # Display the rewritten resume in markdown format
                st.markdown(improved_resume_text)

                # Add a download button for the improved resume
                st.download_button("Download Improved Resume", improved_resume_text, file_name="improved_resume.md")

    else:
        st.error("Google API key is required. Please provide the key in '.env' for local development or Streamlit Secrets for cloud deployment.")

if __name__ == "__main__":
    main()

