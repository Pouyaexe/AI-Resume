from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

def setup_rag_pipeline(vector_store):
    """Set up the custom Retrieval-Augmented Generation pipeline with the LLM."""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        max_tokens=500,
        timeout=None,
        max_retries=2,
    )

    # Feedback Prompt
    feedback_prompt_template = """
    Based on the provided Harvard resume guidelines, provide feedback for improving the resume section. Include suggestions such as quantifying achievements, avoiding personal pronouns, and using active language.

    Guidelines:
    {guide_section}

    Resume Section:
    {resume_section}

    Feedback for Resume Section:
    """

    # Rewriting Prompt
    rewrite_prompt_template = """
    Based on the provided Harvard resume guidelines, rewrite the content of the resume section below. Do not include the section header, only return the rewritten content.

    Guidelines:
    {guide_section}

    Resume Section:
    {resume_section}

    Rewritten Resume Content (without section header):
    """


    # Create prompt templates
    feedback_prompt = PromptTemplate(
        template=feedback_prompt_template,
        input_variables=["resume_section", "guide_section"]
    )

    rewrite_prompt = PromptTemplate(
        template=rewrite_prompt_template,
        input_variables=["resume_section", "guide_section"]
    )

    # Create two LLMChains, one for feedback and one for rewriting
    feedback_chain = LLMChain(
        llm=llm,
        prompt=feedback_prompt
    )

    rewrite_chain = LLMChain(
        llm=llm,
        prompt=rewrite_prompt
    )

    return feedback_chain, rewrite_chain



if __name__ == "__main__":
    pass
