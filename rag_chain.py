"""
Minimal RAG Chain for question answering.

This script demonstrates:
1. Loading existing Chromadb vector store
2. Creating a retriever
3. Building a RAG chain
4. Using a custom prompt template
5. Answering queries using retrieved context
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


def answer_query(query: str) -> str:
    """
    Answer a query using the RAG chain.
    
    Steps:
    1. Load the Chromadb vector store
    2. Create a retriever
    3. Build a RAG chain with custom prompt
    4. Execute the chain and return the answer
    
    Args:
        query (str): The question to answer
        
    Returns:
        str: The answer based on retrieved context
    """
    
    # Step 1: Load the existing Chromadb vector store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
        collection_name="product_embeddings"
    )
    
    # Step 2: Create a retriever from the vector store
    # k=3 means retrieve top 3 relevant chunks
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # Step 3: Define the custom prompt template
    prompt_template = """Answer ONLY using the provided context. If the answer is not in the context, say "I don't have this information."

Context:
{context}

Question: {question}

Answer:"""
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    # Step 4: Initialize the LLM (Gemini)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    
    # Step 5: Build the RAG chain using LCEL (LangChain Expression Language)
    # This is the modern way to build chains
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Execute the chain and return the answer
    answer = rag_chain.invoke(query)
    
    return answer


def main():
    """Test the RAG chain with sample queries."""
    
    print("=" * 60)
    print("🤖 RAG Chain Question Answering")
    print("=" * 60)
    
    # Sample queries
    queries = [
        "What is the price of SmartWatch Pro X?",
        "What is the return policy?",
        "How many hours of battery does Wireless Earbuds Elite have?"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        try:
            answer = answer_query(query)
            print(f"✓ Answer: {answer}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
