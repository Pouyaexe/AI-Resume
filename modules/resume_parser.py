import re

def detect_resume_sections(text):
    """Detect and split resume sections based on common headers."""
    section_headers = ['Education', 'Work Experience', 'Experience', 'Skills', 'Certifications', 'Hobbies', 'Interests', 'Projects', 'Awards']

    # Build regex to match any of the section headers, ignoring case
    regex = r'(?i)(\b(?:' + '|'.join(map(re.escape, section_headers)) + r')\b.*?)(?=\b(?:' + '|'.join(map(re.escape, section_headers)) + r')\b|$)'
    
    sections = re.findall(regex, text, re.DOTALL)
    
    return sections

def process_resume(resume_text, feedback_chain, rewrite_chain, vector_store):
    """
    Process the user's resume, generate both feedback and improvements for each section, and return them separately.
    
    Args:
        resume_text (str): The user's current resume text.
        feedback_chain: The LLM chain for feedback.
        rewrite_chain: The LLM chain for rewriting sections.
        vector_store: The vector store for retrieval.
    
    Returns:
        dict: Two dictionaries, one with feedback and one with improved resume sections.
    """
    
    # Step 1: Parse the resume into sections
    resume_sections = detect_resume_sections(resume_text)
    
    # Dictionaries to store feedback and rewritten resume sections
    feedback = {}
    improved_resume = {}

    # Step 2: Process each section
    for section in resume_sections:
        lines = section.split("\n")
        title = lines[0].strip()  # Section title
        content = "\n".join(lines[1:]).strip()  # Section content

        # Query the vector store to retrieve relevant guidelines for this section
        query = f"How to write an impactful {title.lower()} section in a resume."
        relevant_docs = vector_store.similarity_search(query, k=3)
        guide_text = "\n".join([doc.page_content for doc in relevant_docs])

        # Generate feedback
        feedback_response = feedback_chain.run({
            "resume_section": content,
            "guide_section": guide_text
        })
        feedback[title] = feedback_response

        # Rewriting the resume section
        rewrite_response = rewrite_chain.run({
            "resume_section": content,
            "guide_section": guide_text
        })

        # Remove duplicated section headers
        first_line = rewrite_response.split('\n')[0].strip()
        if first_line.lower().startswith(title.lower()):
            # If the first line is the same as the title, remove it
            rewrite_response = "\n".join(rewrite_response.split('\n')[1:]).strip()

        # Store the rewritten resume section
        improved_resume[title] = f"### {title}\n{rewrite_response}"

    # Step 3: Return both the feedback and the improved resume
    return feedback, improved_resume

def process_full_resume(feedback, full_resume_text, rewrite_chain):
    """
    Generate a rewritten full resume based on feedback from all sections.
    
    Args:
        feedback (dict): Feedback from the LLM for each section.
        full_resume_text (str): The original resume text.
        rewrite_chain: The LLM chain for rewriting the full resume.
    
    Returns:
        str: The rewritten full resume based on the feedback.
    """
    # Combine all feedback into a single string
    feedback_text = "\n\n".join([f"{section}:\n{content}" for section, content in feedback.items()])
    
    # Rewrite the full resume based on the feedback
    rewrite_response = rewrite_chain.run({
        "resume_section": full_resume_text,
        "guide_section": feedback_text  # The feedback is used as guidelines for the full rewrite
    })

    return rewrite_response

if __name__ == "__main__":
    pass