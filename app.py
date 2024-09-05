import os
import streamlit as st
from modules.pdf_utils import extract_pdf_text, clean_extracted_text
from modules.vectorstore_utils import create_vector_store, split_text
from modules.llm_pipeline import setup_rag_pipeline
from modules.resume_parser import process_resume

# Function to get the Google API key from a txt file or environment
def get_google_api_key():
    """Get the Google API key from a txt file or environment."""
    # Check if the key is already set in environment (useful for cloud environments)
    if "GOOGLE_API_KEY" in os.environ:
        return os.getenv("GOOGLE_API_KEY")
    else:
        try:
            # Read the API key from a text file if it exists locally
            with open("apikey.txt", "r") as file:
                api_key = file.read().strip()
                os.environ["GOOGLE_API_KEY"] = api_key  # Set it in the environment for later use
                return api_key
        except FileNotFoundError:
            st.error("API key file not found. Please ensure that 'api_key.txt' exists with the API key.")
            return None

def main():
    st.title("Resume Rewriter Using Harvard Guidelines")

    # Get the API key from file or environment
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
        st.error("Google API key is required. Please provide the key in 'api_key.txt' or set it as an environment variable.")

if __name__ == "__main__":
    main()
