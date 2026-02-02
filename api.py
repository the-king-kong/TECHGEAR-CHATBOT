"""
Beginner-Friendly FastAPI Application for TechGear Chatbot

EXPLANATION FOR BEGINNERS:
==========================
FastAPI is a modern web framework that turns Python functions into a REST API.

What is an API?
- API = Application Programming Interface
- Allows other programs to communicate with your application via HTTP requests
- Uses JSON format for data exchange

How it works:
1. Client sends: POST /chat with JSON {"query": "What is the price?"}
2. FastAPI receives and validates the JSON
3. Calls process_query() from graph.py with the query
4. Gets response from LangGraph workflow
5. Returns JSON response back to client

All endpoints:
- GET  /           → Welcome message
- GET  /health     → Check if API is running
- POST /chat       → Main endpoint for chatbot (MOST IMPORTANT!)
- GET  /docs       → Interactive documentation (Swagger UI)
- GET  /redoc      → Alternative documentation (ReDoc)

Installation:
    pip install fastapi uvicorn

Running:
    python api.py
    (Then visit http://localhost:8000/docs to test)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from pathlib import Path

# Import the LangGraph workflow
from graph import process_query


# ============================================================================
# STEP 1: DEFINE REQUEST AND RESPONSE MODELS (Pydantic)
# ============================================================================
"""
Pydantic models validate JSON structure.

They act like templates that:
- Define expected data fields
- Check data types
- Provide helpful error messages if data is invalid
- Auto-convert JSON to Python objects
"""

class ChatRequest(BaseModel):
    """
    REQUEST MODEL: What clients send to the API
    
    This defines the structure of incoming JSON.
    
    Example:
    {
        "query": "What is the price of SmartWatch Pro X?"
    }
    """
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the price of SmartWatch Pro X?"
            }
        }


class ChatResponse(BaseModel):
    """
    RESPONSE MODEL: What the API sends back
    
    This defines the structure of outgoing JSON.
    
    Example:
    {
        "query": "What is the price of SmartWatch Pro X?",
        "category": "product",
        "response": "₹15,999",
        "status": "success"
    }
    """
    query: str
    response: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the price of SmartWatch Pro X?",
                "response": "₹15,999"
            }
        }


# ============================================================================
# STEP 2: CREATE THE FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="🤖 TechGear Chatbot API",
    description="Intelligent chatbot powered by LangGraph and RAG",
    version="1.0.0"
)


# ============================================================================
# STEP 3: ADD CORS MIDDLEWARE
# ============================================================================
"""
CORS = Cross-Origin Resource Sharing
Allows API to be accessed from web browsers and different domains.
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# STEP 4: DEFINE API ENDPOINTS
# ============================================================================

@app.get("/", response_class=FileResponse)
def root():
    """
    ENDPOINT 1: GET /
    
    Purpose: Serve the interactive web UI for the chatbot
    
    Returns: HTML file with the beautiful frontend interface
    """
    frontend_path = Path(__file__).parent / "frontend.html"
    if frontend_path.exists():
        return FileResponse(str(frontend_path), media_type="text/html")
    else:
        return {
            "message": "🤖 Welcome to TechGear Chatbot API",
            "version": "1.0.0",
            "note": "Frontend UI file (frontend.html) not found",
            "endpoints": {
                "POST /chat": "Send a query to the chatbot",
                "GET /health": "Check if API is running",
                "GET /docs": "Swagger UI documentation"
            }
        }


@app.get("/health")
def health_check():
    """
    ENDPOINT 2: GET /health
    
    Purpose: Health check - verify API is running
    
    Returns: JSON with health status
    """
    chromadb_ready = os.path.exists("./chroma_db")
    
    return {
        "status": "✅ Healthy" if chromadb_ready else "⚠️ Degraded",
        "api": "Running",
        "chromadb": "Ready" if chromadb_ready else "Not initialized - run ingest.py first",
        "message": "Send POST requests to /chat with your queries"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    ENDPOINT 3: POST /chat (⭐ MAIN CHATBOT ENDPOINT)
    
    Purpose: Send a query to the chatbot and get an AI-generated response
    
    How it works:
    1. Receive JSON: {"query": "user's question"}
    2. Validate the JSON structure
    3. Send query to LangGraph workflow (graph.py)
    4. Graph classifies query → routes to RAG or escalation
    5. RAG retrieves context from Chromadb
    6. LLM generates response based on context
    7. Return response as JSON
    
    Request Example:
    {
        "query": "What is the price of SmartWatch Pro X?"
    }
    
    Response Example:
    {
        "query": "What is the price of SmartWatch Pro X?",
        "response": "₹15,999"
    }
    
    Usage with curl:
        curl -X POST "http://localhost:8000/chat" \\
             -H "Content-Type: application/json" \\
             -d '{"query": "What is the price of SmartWatch Pro X?"}'
    
    Usage with Python:
        import requests
        
        response = requests.post(
            "http://localhost:8000/chat",
            json={"query": "What is the price of SmartWatch Pro X?"}
        )
        print(response.json())
    
    Raises:
        HTTPException(400): If query is empty
        HTTPException(500): If processing fails
    """
    
    print(f"\n📥 Received chat request: {request.query}")
    
    # Validate: Query cannot be empty
    if not request.query or not request.query.strip():
        print("❌ Empty query rejected")
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty. Please provide a question."
        )
    
    try:
        # Send to LangGraph workflow
        print(f"🔄 Processing through LangGraph workflow...")
        response_text = process_query(request.query)
        
        print(f"✅ Response generated: {response_text[:50]}...")
        
        # Return formatted response
        return ChatResponse(
            query=request.query,
            response=response_text
        )
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


# ============================================================================
# STEP 5: HELPER FUNCTIONS
# ============================================================================

def infer_category(query: str) -> str:
    """
    Infer query category based on keywords
    
    This is a simple heuristic for categorizing queries:
    - "product": Price, specs, features → RAG Responder
    - "returns": Return, refund, warranty → RAG Responder
    - "general": Other queries → Escalation
    
    Args:
        query (str): User query
        
    Returns:
        str: Category (product, returns, or general)
    """
    query_lower = query.lower()
    
    product_keywords = ["price", "cost", "specs", "features", "product", "watch", "earbuds", "battery", "how much"]
    return_keywords = ["return", "refund", "exchange", "warranty", "broken", "policy"]
    
    if any(kw in query_lower for kw in product_keywords):
        return "product"
    elif any(kw in query_lower for kw in return_keywords):
        return "returns"
    else:
        return "general"


# ============================================================================
# STEP 6: STARTUP AND SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Called when API starts - log initialization"""
    print("\n" + "="*70)
    print("🚀 TECHGEAR CHATBOT API STARTING UP")
    print("="*70)
    print("✅ API initialized and ready!")
    print("\n📚 Available endpoints:")
    print("   GET  /              → Welcome & endpoint info")
    print("   GET  /health        → Health check")
    print("   POST /chat          → Send query (MAIN ENDPOINT)")
    print("   GET  /docs          → Swagger UI interactive docs")
    print("   GET  /redoc         → ReDoc alternative docs")
    print("\n🌐 Open http://localhost:8000/docs to test the API!")
    print("="*70 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Called when API shuts down"""
    print("\n🛑 API shutting down...")


# ============================================================================
# STEP 7: RUN THE SERVER
# ============================================================================

if __name__ == "__main__":
    """
    Run this file to start the API server
    
    Command:
        python api.py
    
    Then visit: http://localhost:8000/docs
    
    To run with custom settings:
        uvicorn api:app --reload --host 0.0.0.0 --port 8000
    """
    
    import uvicorn
    
    print("\n" + "="*70)
    print("🌐 STARTING FASTAPI SERVER")
    print("="*70)
    print("📌 Starting command: uvicorn api:app --reload")
    print("📌 Server: http://localhost:8000")
    print("📌 API Docs: http://localhost:8000/docs")
    print("\n💡 Try the /chat endpoint with:")
    print('   {"query": "What is the price of SmartWatch Pro X?"}')
    print("="*70 + "\n")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
