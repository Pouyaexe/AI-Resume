import streamlit as st

def display_original_resume(resume_text):
    """
    Display the original resume in the UI.
    
    Args:
        resume_text (str): The original resume text.
    """
    st.write("### Original Resume:")
    st.text_area("Resume Text", resume_text, height=300)

def display_feedback(feedback):
    """
    Display the feedback for the resume.
    
    Args:
        feedback (dict): A dictionary of feedback for each section of the resume.
    """
    st.markdown("### Feedback for Your Resume")
    feedback_text = "\n\n".join([f"**{section}**:\n{content}" for section, content in feedback.items()])
    st.markdown(feedback_text)

def display_rewritten_resume(full_resume):
    """
    Display the full rewritten resume in Markdown format.
    
    Args:
        full_resume (str): The full resume text in Markdown format.
    """
    st.markdown("### Full Rewritten Resume (Markdown format)")
    st.markdown(full_resume)
