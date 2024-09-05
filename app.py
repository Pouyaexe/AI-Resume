import os
from dotenv import load_dotenv  # Import the dotenv package
import streamlit as st
from modules.pdf_utils import extract_pdf_text, clean_extracted_text
from modules.vectorstore_utils import create_vector_store, split_text
from modules.llm_pipeline import setup_rag_pipeline
from modules.resume_parser import process_resume

# Load environment variables from .env file
load_dotenv()  # This will load the .env file and set environment variables

# Retrieve the Google API key from the environment
api_key = os.getenv("GOOGLE_API_KEY")

# Define a function to get the API key, either from .env or user input
def get_google_api_key():
    """Get the Google API key from the environment or prompt the user for input."""
    if not api_key:
        # Ask the user for the API key if not found in environment
        api_key_input = st.text_input("Please enter your Google API key", type="password")
        if api_key_input:
            # Set the API key in the environment for the rest of the app
            os.environ["GOOGLE_API_KEY"] = api_key_input
            return api_key_input
        else:
            st.warning("Google API key is required to run the app.")
            return None
    else:
        return api_key

def main():
    st.title("Resume Rewriter Using Harvard Guidelines")

    # Get the API key from environment or user input
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
        st.error("Google API key is required. Please provide the key.")

if __name__ == "__main__":
    main()
