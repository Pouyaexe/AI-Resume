from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

def setup_rag_pipeline(vector_store):
    """Set up the Retrieval-Augmented Generation pipeline with the LLM."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        max_tokens=500,
        timeout=None,
        max_retries=2,
    )

    prompt_template = """
    Based on the provided Harvard resume guidelines, rewrite the resume section with specific improvements, such as quantifying achievements, avoiding personal pronouns, and using active language. Ensure the rewriting is according to best resume practices.

    Guidelines:
    {guide_section}

    Resume Section:
    {resume_section}

    Rewritten Resume Section:
    """
    prompt_template = """
    You are a professional resume writer. You have been asked to rewrite the resume section 
    
    """        
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["resume_section", "guide_section"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(),
        return_source_documents=True
    )

    return qa_chain
