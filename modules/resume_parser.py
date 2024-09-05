import re

def detect_resume_sections(text):
    """Detect and split resume sections based on common headers."""
    section_headers = ['Education', 'Work Experience', 'Experience', 'Skills', 'Certifications', 'Hobbies', 'Interests', 'Projects', 'Awards']

    # Build regex to match any of the section headers, ignoring case
    regex = r'(?i)(\b(?:' + '|'.join(map(re.escape, section_headers)) + r')\b.*?)(?=\b(?:' + '|'.join(map(re.escape, section_headers)) + r')\b|$)'
    
    sections = re.findall(regex, text, re.DOTALL)
    
    return sections

def process_resume(resume_text, qa_chain, vector_store):
    """Process resume, detect sections, and rewrite them."""
    resume_sections = detect_resume_sections(resume_text)
    improved_resume = {}

    for section in resume_sections:
        lines = section.split("\n")
        title = lines[0].strip()
        content = "\n".join(lines[1:]).strip()

        query = f"How to write an impactful {title.lower()} section in a resume."
        relevant_docs = vector_store.similarity_search(query, k=3)
        guide_text = "\n".join([doc.page_content for doc in relevant_docs])

        response = qa_chain.invoke({
            "query": content,  
            "resume_section": content,
            "guide_section": guide_text
        })

        improved_resume[title] = response["result"]

    return improved_resume
