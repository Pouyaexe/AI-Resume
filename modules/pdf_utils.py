import pdfplumber
import re

def extract_pdf_text(pdf_file):
    """Extract text from a PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def clean_extracted_text(text):
    """Clean extracted text by removing extra spaces and newlines."""
    cleaned_text = re.sub(r'\n{2,}', '\n', text)
    return cleaned_text

if __name__ == "__main__":
    pass