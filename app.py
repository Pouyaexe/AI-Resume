import re
import pickle
import numpy as np
import faiss
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.docstore import InMemoryDocstore
from langchain.vectorstores.faiss import FAISS as FAISS_LangChain
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Step 1: Load Markdown Guide
def load_markdown_guide(md_path):
    """Load the LLM-ready Harvard resume guide from a Markdown file."""
    with open(md_path, 'r') as file:
        guide_text = file.read()
    return guide_text

# Step 2: Split Text into Chunks
def split_text(text, chunk_size=500, chunk_overlap=50):
    """Split text into chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_text(text)
    return chunks

# Step 3: Create Embeddings and Vector Store
def create_vector_store(chunks):
    """Create a FAISS vector store from text chunks."""
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Create embeddings for all chunks
    chunk_embeddings = embeddings.embed_documents(chunks)
    dimension = len(chunk_embeddings[0])
    
    # Initialize FAISS index
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(chunk_embeddings))
    
    # Create a docstore to store the chunks
    docstore = InMemoryDocstore({i: Document(page_content=chunk) for i, chunk in enumerate(chunks)})
    
    # Map index to docstore IDs
    index_to_docstore_id = {i: i for i in range(len(chunks))}
    
    # Initialize the FAISS vector store
    vector_store = FAISS_LangChain(embedding_function=embeddings, index=index, docstore=docstore, index_to_docstore_id=index_to_docstore_id)
    
    return vector_store

# Step 4: Set Up RAG Pipeline
def setup_rag_pipeline(vector_store):
    """Set up the Retrieval-Augmented Generation pipeline."""
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

# Step 5: Process User Resume
def process_resume(resume_text, qa_chain, vector_store):
    """
    Process the user's resume and generate improvements based on the Harvard guide.
    
    Args:
        resume_text (str): The user's current resume text.
        qa_chain: The RetrievalQA chain.
        vector_store: The vector store for retrieval.
    
    Returns:
        dict: A dictionary with original and improved resume sections.
    """
    # Simple parser to split resume into sections based on headers
    sections = re.split(r'\n(?=[A-Z][A-Za-z\s]+:)', resume_text)
    resume_sections = {}
    for section in sections:
        if ':' in section:
            title, content = section.split(':', 1)
            resume_sections[title.strip()] = content.strip()

    improved_resume = {}

    for title, content in resume_sections.items():
        print(f"Processing section: {title}")
        # Query the vector store for relevant guidance
        query = f"How to write an impactful {title.lower()} section in a resume."
        relevant_docs = vector_store.similarity_search(query, k=3)
        guide_text = "\n".join([doc.page_content for doc in relevant_docs])

        # Print retrieved guide text for debugging
        print(f"Retrieved guide text for {title}:\n{guide_text}\n")

        # Generate improved section using RAG
        response = qa_chain.invoke({
            "query": content,  # The resume section text serves as the query
            "resume_section": content,
            "guide_section": guide_text
        })

        # Extract the relevant output
        improved_resume[title] = response["result"]

    return improved_resume


# Step 6: Main Execution
if __name__ == "__main__":
    # Paths and setup
    md_path = "harvard_resume_guide.md"  # Update with your Markdown file path
    guide_text = load_markdown_guide(md_path)
    chunks = split_text(guide_text)
    print(f"Total chunks created: {len(chunks)}")

    vector_store = create_vector_store(chunks)
    print("Vector store created.")

    qa_chain = setup_rag_pipeline(vector_store)
    print("RAG pipeline set up.")

    # Sample resume
    sample_resume = """
    EDUCATION:
    Bachelor of Science in Computer Science, XYZ University, 2018-2022

    WORK EXPERIENCE:
    Software Engineer at ABC Corp, 2022-Present
    - Developed web applications using JavaScript and React.
    - Collaborated with cross-functional teams to define project requirements.

    SKILLS:
    - Programming Languages: Python, JavaScript, Java
    - Frameworks: React, Django, Flask
    """

    improved = process_resume(sample_resume, qa_chain, vector_store)

    print("\n--- Improved Resume ---\n")
    for section, content in improved.items():
        print(f"{section}:\n{content}\n")
