"""
Fast Data Ingestion Script - Simplified version without heavy imports
"""
import os
os.environ['PYTHONUNBUFFERED'] = '1'

print("🚀 Starting Fast Ingestion Pipeline...")

# Import only what we need
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

def fast_ingest():
    """Lightweight ingestion without RecursiveCharacterTextSplitter"""
    
    print("\n📖 Loading product data...")
    with open('data/product_info.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"✓ Loaded: {len(text)} characters")
    
    # Simple chunking
    print("\n✂️  Splitting text into chunks...")
    chunk_size = 500
    chunks = []
    for i in range(0, len(text), chunk_size - 100):
        chunk = text[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    
    print(f"✓ Created {len(chunks)} chunks")
    
    # Create embeddings
    print("\n🤖 Creating embeddings...")
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        print("✓ Embedding model initialized")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Store in ChromaDB
    print("\n💾 Storing in ChromaDB...")
    try:
        vector_store = Chroma.from_texts(
            texts=chunks,
            embedding=embeddings,
            persist_directory="./chroma_db"
        )
        print("✓ Successfully stored embeddings in ChromaDB")
        print(f"✓ Database persisted to: ./chroma_db")
        return True
    except Exception as e:
        print(f"❌ Error storing embeddings: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("FAST RAG DATA INGESTION PIPELINE")
    print("=" * 70)
    
    success = fast_ingest()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ INGESTION SUCCESSFUL!")
        print("=" * 70)
        print("\n✨ Your chatbot is ready to answer product questions!")
        print("Run: uvicorn api:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("\n" + "=" * 70)
        print("❌ INGESTION FAILED")
        print("=" * 70)
        print("Please check your API key and try again.")
