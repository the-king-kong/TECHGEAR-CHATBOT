"""
Beginner-friendly RAG data ingestion script.

This script demonstrates the core steps of building a Retrieval-Augmented Generation (RAG) system:
1. Load text data from a file
2. Split text into manageable chunks
3. Generate embeddings for each chunk
4. Store embeddings in a vector database (Chromadb)

Requirements:
- langchain
- langchain-community
- langchain-google-genai (for Gemini embeddings)
- chromadb
"""

# Import required libraries
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
import os


def load_document(file_path):
    """
    Load text content from a file.
    
    Args:
        file_path (str): Path to the text file to load
        
    Returns:
        str: Content of the file
    """
    print(f"📖 Loading document from: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    print(f"✓ Document loaded successfully ({len(content)} characters)")
    return content


def split_text_into_chunks(text, chunk_size=500, chunk_overlap=100):
    """
    Split text into smaller chunks using LangChain's RecursiveCharacterTextSplitter.
    
    This splitter recursively tries different separators to keep text semantically meaningful.
    
    Args:
        text (str): The text to split
        chunk_size (int): Maximum size of each chunk in characters (default: 500)
        chunk_overlap (int): Number of characters to overlap between chunks (default: 100)
        
    Returns:
        list: List of text chunks
    """
    print(f"\n✂️  Splitting text into chunks (size={chunk_size}, overlap={chunk_overlap})")
    
    # Create a text splitter with sensible defaults
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # These separators are tried in order to keep text coherent
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # Split the text
    chunks = splitter.split_text(text)
    
    print(f"✓ Text split into {len(chunks)} chunks")
    
    # Show a sample chunk
    if chunks:
        print(f"\nSample chunk (first 100 chars):\n{chunks[0][:100]}...")
    
    return chunks


def create_embeddings_and_store(chunks, persist_directory="./chroma_db"):
    """
    Create embeddings for text chunks and store them in Chromadb.
    
    This function:
    1. Initializes a Gemini embedding model
    2. Creates a Chromadb vector store
    3. Stores the chunks with their embeddings persistently
    
    Args:
        chunks (list): List of text chunks to embed
        persist_directory (str): Directory to persist the Chromadb data
        
    Returns:
        Chroma: The Chromadb vector store instance
    """
    print(f"\n🤖 Creating embeddings using Gemini API...")
    
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set")
        print("   Set it with: export GOOGLE_API_KEY='your-api-key'")
        print("   Get your key from: https://aistudio.google.com/app/apikey")
    
    # Initialize the Gemini embedding model
    # This uses the free Gemini API for generating embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    print(f"✓ Embedding model initialized")
    
    print(f"\n💾 Storing embeddings in Chromadb...")
    print(f"   Persist directory: {persist_directory}")
    
    # Create a Chromadb vector store with the chunks and embeddings
    # persist_directory ensures the data is saved to disk and can be reloaded
    vector_store = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name="product_embeddings"
    )
    
    print(f"✓ Embeddings stored successfully in Chromadb")
    print(f"✓ Total chunks indexed: {len(chunks)}")
    
    return vector_store


def main():
    """
    Main execution flow: Load → Split → Embed → Store
    """
    print("=" * 60)
    print("🚀 RAG Data Ingestion Pipeline")
    print("=" * 60)
    
    try:
        # Step 1: Load the document
        file_path = "data/product_info.txt"
        text_content = load_document(file_path)
        
        # Step 2: Split into chunks
        chunks = split_text_into_chunks(text_content, chunk_size=500, chunk_overlap=100)
        
        # Step 3 & 4: Create embeddings and store in Chromadb
        vector_store = create_embeddings_and_store(chunks)
        
        # Quick test: Perform a sample search
        print(f"\n🔍 Testing retrieval with a sample query...")
        results = vector_store.similarity_search("What is the price of SmartWatch?", k=2)
        
        print(f"\nTop search result:")
        print(f"  {results[0].page_content[:100]}...")
        
        print("\n" + "=" * 60)
        print("✅ Pipeline completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("  - Use the 'vector_store' to retrieve relevant chunks")
        print("  - Feed retrieved chunks to an LLM for question answering")
        print("  - The Chromadb data persists in './chroma_db' folder")
        
    except FileNotFoundError as e:
        print(f"❌ Error: Could not find file - {e}")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
