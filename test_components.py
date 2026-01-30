"""
Diagnostic script to test each component of the RAG pipeline independently.
This helps identify which part is working and which needs fixing.
"""

import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def test_document_loading():
    """Test 1: Document Loading"""
    print("\n" + "=" * 60)
    print("TEST 1: 📖 DOCUMENT LOADING")
    print("=" * 60)
    
    file_path = "data/product_info.txt"
    
    try:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        print(f"✅ Document loaded successfully")
        print(f"   File: {file_path}")
        print(f"   Size: {len(content)} characters")
        print(f"   Lines: {len(content.split(chr(10)))}")
        print(f"\n📄 Content preview (first 200 chars):")
        print(f"   {content[:200]}...")
        
        return content
        
    except Exception as e:
        print(f"❌ Error loading document: {e}")
        return None


def test_chunking_logic(content):
    """Test 2: Chunking Logic"""
    print("\n" + "=" * 60)
    print("TEST 2: ✂️  CHUNKING LOGIC")
    print("=" * 60)
    
    if not content:
        print("❌ No content to chunk")
        return None
    
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = splitter.split_text(content)
        
        print(f"✅ Chunking successful")
        print(f"   Total chunks created: {len(chunks)}")
        print(f"   Chunk size range: {min(len(c) for c in chunks)} - {max(len(c) for c in chunks)} characters")
        
        for i, chunk in enumerate(chunks):
            print(f"\n📦 Chunk {i+1} ({len(chunk)} chars):")
            print(f"   {chunk[:100]}...")
        
        return chunks
        
    except Exception as e:
        print(f"❌ Error during chunking: {e}")
        return None


def test_vector_db_persistence():
    """Test 3: Vector DB Persistence"""
    print("\n" + "=" * 60)
    print("TEST 3: 💾 VECTOR DB PERSISTENCE")
    print("=" * 60)
    
    persist_dir = "./chroma_db"
    
    try:
        # Check if Chromadb directory exists
        if os.path.exists(persist_dir):
            print(f"✅ Chromadb directory exists: {persist_dir}")
            
            # List contents
            contents = os.listdir(persist_dir)
            print(f"   Contents: {contents}")
            
            # Try to load the existing vector store
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            vector_store = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings,
                collection_name="product_embeddings"
            )
            
            print(f"✅ Successfully loaded existing Chromadb")
            print(f"   Collection: product_embeddings")
            
            # Test a query
            results = vector_store.similarity_search("SmartWatch", k=1)
            if results:
                print(f"✅ Query test successful")
                print(f"   Found result: {results[0].page_content[:80]}...")
            
        else:
            print(f"⚠️  Chromadb directory not found: {persist_dir}")
            print(f"   (This is normal if you haven't run ingest.py yet)")
        
    except Exception as e:
        print(f"❌ Error accessing Chromadb: {e}")


def main():
    """Run all component tests"""
    print("\n🔬 RAG PIPELINE COMPONENT DIAGNOSTICS")
    
    # Test 1: Document Loading
    content = test_document_loading()
    
    # Test 2: Chunking Logic
    if content:
        chunks = test_chunking_logic(content)
    
    # Test 3: Vector DB Persistence
    test_vector_db_persistence()
    
    print("\n" + "=" * 60)
    print("✅ DIAGNOSTIC TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()