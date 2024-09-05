import os
import streamlit as st
from dotenv import load_dotenv  # Import for local environment
from modules.pdf_utils import extract_pdf_text, clean_extracted_text
from modules.vectorstore_utils import create_vector_store, split_text
from modules.llm_pipeline import setup_rag_pipeline
from modules.resume_parser import process_resume

# Function to get the Google API key
def get_google_api_key():
    """Get the Google API key either from Streamlit secrets (Cloud) or .env (Local)."""
    if "GOOGLE_API_KEY" in os.environ:
        # If running locally and the API key is already set in the environment
        return os.getenv("GOOGLE_API_KEY")
    elif "GOOGLE_API_KEY" in st.secrets:
        # If running on Streamlit Cloud and using secrets
        api_key = st.secrets["GOOGLE_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = api_key  # Set it in the environment
        return api_key
    else:
        # Attempt to load from a .env file if running locally
        load_dotenv()  # This will load the .env file into environment variables
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            return api_key
        else:
            st.error("Google API key is required but not found. Please add it to .env for local or Secrets for Streamlit Cloud.")
            return None

def main():
    st.title("Resume Rewriter Using Harvard Guidelines")

    # Get the API key from environment or secrets
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

                chunks = split_text(guide_text)
                vector_store = create_vector_store(chunks)
                qa_chain = setup_rag_pipeline(vector_store)

                improved_resume = process_resume(resume_text, qa_chain, vector_store)

                improved_resume_text = "\n\n".join([f"### {section}:\n{content}" for section, content in improved_resume.items()])
                st.markdown("### Improved Resume (Markdown format):")
                st.markdown(improved_resume_text)

                st.download_button("Download Improved Resume", improved_resume_text, file_name="improved_resume.md")
    else:
        st.error("Google API key is required. Please provide the key in `.env` for local development or Streamlit Secrets for cloud deployment.")

if __name__ == "__main__":
    main()
