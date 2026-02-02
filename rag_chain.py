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
import os

# Mock product database for fallback
MOCK_DATA = """
Product: SmartWatch Pro X
Price: ₹15,999 | Features: Heart rate, GPS, 7-day battery, water resistant 50m
Warranty: 1 year standard, 2 years extended (₹1,999)

Product: Wireless Earbuds Elite
Price: ₹4,999 | Features: ANC, 24-hour battery, Bluetooth 5.2
Warranty: 6 months

Product: Power Bank Ultra 20000mAh
Price: ₹2,499 | Features: Fast charging 22.5W, USB-C & USB-A
Warranty: 1 year

Product: USB-C Fast Charging Cable
Price: ₹599 | Features: 3m length, 65W fast charging, durable nylon braided
Warranty: 2 years

Product: Wireless Charging Pad Pro
Price: ₹1,999 | Features: 15W fast wireless charging, LED indicator, non-slip surface
Warranty: 1 year

Product: Bluetooth Speaker Mini
Price: ₹1,499 | Features: 360° sound, IPX7 waterproof, 12-hour battery
Warranty: 1 year

Product: Phone Stand Adjustable
Price: ₹799 | Features: Aluminum alloy, 360° rotation, adjustable height
Warranty: Lifetime

Product: Screen Protector Glass (Pack of 2)
Price: ₹399 | Features: Tempered glass, 9H hardness, anti-fingerprint coating
Warranty: 6 months

Product: Phone Case Premium
Price: ₹899 | Features: Shock-absorbing TPU, sleek design, 5 color options
Warranty: 6 months

Product: LED Ring Light
Price: ₹2,999 | Features: 10 brightness levels, USB powered, 3 color modes
Warranty: 1 year

Return Policy: 7-day no-questions-asked. Refund in 5-7 business days.
Total Products Available: 10 products in our catalog
Support: Mon-Sat, 9AM-6PM IST | support@techgear.com
"""

def answer_query_with_fallback(query: str, llm) -> str:
    """Answer using mock data as fallback."""
    prompt_template = """Answer ONLY using the provided context. If the answer is not in the context, say "I don't have this information."

Context:
{context}

Question: {query}

Answer:"""
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "query"]
    )
    
    rag_chain = (
        {"context": lambda x: MOCK_DATA, "query": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain.invoke(query)


def answer_query(query: str) -> str:
    """
    Answer a query using the RAG chain with fallback to mock data.
    
    Steps:
    1. Try to load the Chromadb vector store
    2. If ChromaDB is empty or unavailable, use mock data
    3. Create a retriever from the vector store or use mock data
    4. Build a RAG chain with custom prompt
    5. Execute the chain and return the answer
    
    Args:
        query (str): The question to answer
        
    Returns:
        str: The answer based on retrieved context
    """
    
    # Initialize the LLM (Gemini)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    
    try:
        # Try to load ChromaDB
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings,
            collection_name="product_embeddings"
        )
        
        # Check if vector store has data
        collection = vector_store._collection
        if collection.count() == 0:
            print("⚠️  ChromaDB is empty, using mock data")
            return answer_query_with_fallback(query, llm)
        
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
        
        # Step 5: Build the RAG chain using LCEL (LangChain Expression Language)
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
        
    except Exception as e:
        print(f"⚠️  ChromaDB error: {e}. Using mock data...")
        return answer_query_with_fallback(query, llm)


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
