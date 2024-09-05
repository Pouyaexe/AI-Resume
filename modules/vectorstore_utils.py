import faiss
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore import InMemoryDocstore
from langchain.vectorstores.faiss import FAISS as FAISS_LangChain
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np

def split_text(text, chunk_size=500, chunk_overlap=50):
    """Split text into chunks for vectorization."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_text(text)
    return chunks

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


if __name__ == "__main__":
    pass