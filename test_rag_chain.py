"""
Diagnostic script to test each component of the RAG chain independently.
This verifies: 1. Retriever setup, 2. Prompt template, 3. Model integration, 4. Chain construction
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


def test_retriever_setup():
    """TEST 1: Verify Retriever Setup"""
    print("\n" + "=" * 70)
    print("TEST 1: 🔍 RETRIEVER SETUP")
    print("=" * 70)
    
    try:
        # Check if Chromadb exists
        persist_dir = "./chroma_db"
        if not os.path.exists(persist_dir):
            print(f"❌ Chromadb directory not found: {persist_dir}")
            return None
        
        print(f"✅ Chromadb directory found: {persist_dir}")
        
        # Load embeddings
        print("\n📌 Loading embedding model...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        print(f"✅ Embeddings model loaded: models/embedding-001")
        
        # Load vector store
        print("\n📌 Loading vector store...")
        vector_store = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings,
            collection_name="product_embeddings"
        )
        print(f"✅ Vector store loaded successfully")
        
        # Create retriever
        print("\n📌 Creating retriever (k=3)...")
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        print(f"✅ Retriever created with k=3")
        
        # Test retriever with a sample query
        print("\n📌 Testing retriever with sample query: 'price'")
        test_docs = retriever.invoke("price")
        print(f"✅ Retriever returned {len(test_docs)} documents")
        
        for i, doc in enumerate(test_docs):
            print(f"\n   📄 Document {i+1}:")
            print(f"      Content: {doc.page_content[:100]}...")
            print(f"      Length: {len(doc.page_content)} chars")
        
        return retriever
        
    except Exception as e:
        print(f"❌ Error in retriever setup: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_prompt_template():
    """TEST 2: Verify Prompt Template"""
    print("\n" + "=" * 70)
    print("TEST 2: 📝 PROMPT TEMPLATE")
    print("=" * 70)
    
    try:
        # Define the prompt template
        prompt_template = """Answer ONLY using the provided context. If the answer is not in the context, say "I don't have this information."

Context:
{context}

Question: {question}

Answer:"""
        
        print(f"✅ Prompt template defined")
        print(f"\n📋 Template preview:")
        print(f"{prompt_template}")
        
        # Create PromptTemplate object
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        print(f"\n✅ PromptTemplate object created")
        print(f"   Input variables: {prompt.input_variables}")
        
        # Test the template with sample data
        print(f"\n📌 Testing prompt template with sample data...")
        test_context = "SmartWatch Pro X costs ₹15,999"
        test_question = "What is the price of SmartWatch Pro X?"
        
        formatted_prompt = prompt.format(context=test_context, question=test_question)
        print(f"✅ Prompt formatted successfully")
        print(f"\n📄 Formatted prompt preview:")
        print(formatted_prompt)
        
        return prompt
        
    except Exception as e:
        print(f"❌ Error in prompt template: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_model_integration():
    """TEST 3: Verify Model Integration"""
    print("\n" + "=" * 70)
    print("TEST 3: 🤖 MODEL INTEGRATION")
    print("=" * 70)
    
    try:
        # Check API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print(f"❌ GOOGLE_API_KEY not set")
            return None
        
        print(f"✅ GOOGLE_API_KEY is set (length: {len(api_key)} chars)")
        
        # Initialize LLM
        print(f"\n📌 Initializing ChatGoogleGenerativeAI...")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            max_tokens=256
        )
        print(f"✅ LLM initialized: gemini-2.0-flash")
        print(f"   Temperature: 0 (deterministic)")
        print(f"   Max tokens: 256")
        
        # Test the model with a simple message
        print(f"\n📌 Testing LLM with a simple message...")
        test_response = llm.invoke("Say 'RAG Chain Test Successful'")
        print(f"✅ LLM response received")
        print(f"   Response: {test_response.content}")
        
        return llm
        
    except Exception as e:
        print(f"❌ Error in model integration: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_chain_construction(retriever, prompt, llm):
    """TEST 4: Verify Chain Construction"""
    print("\n" + "=" * 70)
    print("TEST 4: ⛓️  CHAIN CONSTRUCTION")
    print("=" * 70)
    
    if not all([retriever, prompt, llm]):
        print(f"❌ Missing required components for chain construction")
        return None
    
    try:
        # Define format_docs function
        print(f"✅ Defining format_docs function...")
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        print(f"✅ format_docs function defined")
        
        # Build the RAG chain using LCEL
        print(f"\n📌 Building RAG chain using LCEL...")
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        print(f"✅ RAG chain constructed successfully")
        print(f"   Chain type: RunnableSequence (LCEL)")
        
        # Test the chain with a sample query
        print(f"\n📌 Testing chain with sample query: 'What is SmartWatch Pro X price?'")
        test_query = "What is SmartWatch Pro X price?"
        
        answer = rag_chain.invoke(test_query)
        print(f"✅ Chain execution successful")
        print(f"   Query: {test_query}")
        print(f"   Answer: {answer}")
        
        return rag_chain
        
    except Exception as e:
        print(f"❌ Error in chain construction: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all component tests"""
    print("\n" + "=" * 70)
    print("🔬 RAG CHAIN COMPONENT DIAGNOSTICS")
    print("=" * 70)
    
    # Test 1: Retriever Setup
    retriever = test_retriever_setup()
    
    # Test 2: Prompt Template
    prompt = test_prompt_template()
    
    # Test 3: Model Integration
    llm = test_model_integration()
    
    # Test 4: Chain Construction
    if all([retriever, prompt, llm]):
        rag_chain = test_chain_construction(retriever, prompt, llm)
    else:
        print("\n⚠️  Skipping chain construction test (missing components)")
        rag_chain = None
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 70)
    print(f"1. Retriever Setup:     {'✅ PASS' if retriever else '❌ FAIL'}")
    print(f"2. Prompt Template:     {'✅ PASS' if prompt else '❌ FAIL'}")
    print(f"3. Model Integration:   {'✅ PASS' if llm else '❌ FAIL'}")
    print(f"4. Chain Construction:  {'✅ PASS' if rag_chain else '❌ FAIL'}")
    print("=" * 70)


if __name__ == "__main__":
    main()