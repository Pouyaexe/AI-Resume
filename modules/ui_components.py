import streamlit as st


def display_original_resume(resume_text):
    """
    Display the original resume in the UI.

    Args:
        resume_text (str): The original resume text.
    """
    st.subheader("📝 Original Resume")
    st.text_area("Resume Text", resume_text, height=300)


def display_feedback(feedback):
    """
    Display the feedback for the resume using native Streamlit containers and formatting.

    Args:
        feedback (dict): A dictionary of feedback for each section of the resume.
    """
    st.divider()  # Use a divider to visually separate sections
    st.header("🛠 Feedback for Your Resume", divider="gray")

    # Display feedback using native Streamlit containers
    for section, content in feedback.items():
        with st.container():
            st.subheader(f"📌 Feedback for Resume '{section}' Section", divider=True)
            st.write(content.strip())  # Avoid extra lines or blank feedback


def display_rewritten_resume(full_resume):
    """
    Display the full rewritten resume in Markdown format using native Streamlit formatting.

    Args:
        full_resume (str): The full resume text in Markdown format.
    """
    st.divider()  # Use a divider to separate sections
    st.header("✨ Full Rewritten Resume (Markdown format)", divider="red")
    st.markdown(full_resume)
    st.divider()  # Add a divider at the end
