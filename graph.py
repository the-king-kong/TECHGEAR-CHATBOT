"""
LangGraph-based Multi-Node Workflow for Intelligent Query Routing

EXPLANATION FOR BEGINNERS:
=========================
LangGraph is a library that helps build workflows with multiple steps (nodes).
Instead of a simple function call, you define:
  1. NODES: Individual processing steps
  2. STATE: Information passed between nodes
  3. EDGES: How nodes connect and when to move to the next node

Think of it like a flowchart:
  Query → Classifier Node → (decision) → RAG Node or Escalation Node → Output

This script creates a customer support chatbot that:
  - Classifies user queries into categories
  - Routes to appropriate responder
  - Escalates complex queries when needed
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from rag_chain import answer_query


# ============================================================================
# STEP 1: DEFINE THE GRAPH STATE
# ============================================================================
# State is a TypedDict that holds all information passed between nodes
# Think of it as a data container that travels through the workflow

class GraphState(TypedDict):
    """
    This defines what information is available in the workflow.
    
    Attributes:
        query (str): The user's original question
        category (str): Classification result ("product", "returns", "general", "greeting")
        context (str): Retrieved context from RAG
        response (str): Final answer to return to user
        escalation_reason (str): Why the query was escalated (if applicable)
        is_greeting (bool): Whether the query is a greeting
    """
    query: str
    category: str
    context: str
    response: str
    escalation_reason: str
    is_greeting: bool


# ============================================================================
# STEP 2: DEFINE THE NODES (Processing Steps)
# ============================================================================

def greeting_node(state: GraphState) -> GraphState:
    """
    NODE 0: GREETING NODE
    
    Purpose: Detect if the user is saying hello/hi and respond with a greeting
    
    How it works:
      1. Checks if query contains greeting keywords (hello, hi, hey, etc.)
      2. If yes, returns a friendly greeting
      3. If no, passes through for classification
    
    Args:
        state (GraphState): Current workflow state
        
    Returns:
        GraphState: Updated state with is_greeting flag
    """
    
    print("\n" + "=" * 70)
    print("👋 NODE 0: GREETING CHECK")
    print("=" * 70)
    
    query = state["query"].lower().strip()
    print(f"📥 Input Query: {query}")
    
    # Check for greeting keywords
    greeting_keywords = [
        "hello", "hi", "hey", "hiya", "greetings", "wassup", 
        "what's up", "how are you", "howdy", "namaste", "salaam"
    ]
    
    is_greeting_query = any(keyword in query for keyword in greeting_keywords)
    
    if is_greeting_query:
        print("✅ Detected greeting!")
        state["is_greeting"] = True
        
        # Greeting responses
        greetings = [
            "👋 Hello there! Welcome to TechGear! How can I help you today?",
            "🎉 Hi! Great to see you! Looking for tech products or information?",
            "😊 Hey! Welcome to TechGear support. What can I assist you with?",
            "👋 Hello! I'm here to help. Ask me about our products, pricing, or policies!",
            "🤖 Hi there! I'm TechGear's AI assistant. How can I serve you?"
        ]
        
        import random
        state["response"] = random.choice(greetings)
        state["category"] = "greeting"
        
        print(f"   Response: {state['response']}")
    else:
        print("❌ Not a greeting, proceeding to classification...")
        state["is_greeting"] = False
    
    return state

def classifier_node(state: GraphState) -> GraphState:
    """
    NODE 1: CLASSIFIER NODE
    
    Purpose: Analyze the user query and categorize it into one of three types:
      - "product": Questions about products (price, features, specs)
      - "returns": Questions about return policy or refunds
      - "general": Other questions
    
    How it works:
      1. Takes the user query from state
      2. Sends it to Gemini LLM with a classification prompt
      3. Extracts the category from LLM response
      4. Updates the state with the category
      5. Returns the updated state
    
    Args:
        state (GraphState): Current workflow state containing the query
        
    Returns:
        GraphState: Updated state with category field populated
    """
    
    print("\n" + "=" * 70)
    print("🔍 NODE 1: CLASSIFIER NODE")
    print("=" * 70)
    
    query = state["query"]
    print(f"📥 Input Query: {query}")
    
    # Initialize the LLM (Gemini)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    
    # Create a prompt to classify the query
    classification_prompt = PromptTemplate(
        template="""Categorize this query into EXACTLY ONE of these categories:
        
Categories:
- "product": Questions about product prices, features, specifications
- "returns": Questions about return policy, refunds, warranty
- "general": Other questions or general inquiries

Query: {query}

Respond with ONLY the category name in quotes (e.g., "product" or "returns").
Do not include any other text.""",
        input_variables=["query"]
    )
    
    # Format the prompt
    formatted_prompt = classification_prompt.format(query=query)
    
    # Call the LLM to classify
    response = llm.invoke(formatted_prompt)
    category_text = response.content.strip().lower()
    
    # Clean up the response (remove quotes if present)
    category = category_text.replace('"', '').strip()
    
    # Validate the category
    valid_categories = ["product", "returns", "general"]
    if category not in valid_categories:
        category = "general"  # Default to general if unclear
    
    print(f"✅ Classification Result: '{category}'")
    print(f"   LLM Response: {category_text}")
    
    # Update state with the category
    state["category"] = category
    
    return state


def rag_responder_node(state: GraphState) -> GraphState:
    """
    NODE 2: RAG RESPONDER NODE
    
    Purpose: Answer the query using the RAG chain and Chromadb
    
    How it works:
      1. Takes the query from state
      2. Calls answer_query() from rag_chain.py
      3. RAG chain retrieves relevant context from Chromadb
      4. LLM generates answer based on context
      5. Stores the answer in state
      6. Returns updated state
    
    Args:
        state (GraphState): Current workflow state containing the query
        
    Returns:
        GraphState: Updated state with response field populated
    """
    
    print("\n" + "=" * 70)
    print("🤖 NODE 2: RAG RESPONDER NODE")
    print("=" * 70)
    
    query = state["query"]
    category = state["category"]
    
    print(f"📥 Input Query: {query}")
    print(f"📥 Category: {category}")
    
    try:
        # Call the RAG chain to get the answer
        print(f"🔄 Calling RAG chain...")
        answer = answer_query(query)
        
        print(f"✅ RAG Response Generated")
        print(f"   Answer: {answer}")
        
        # Update state with the response
        state["response"] = answer
        
    except Exception as e:
        print(f"❌ Error in RAG responder: {e}")
        state["response"] = f"I encountered an error while processing your query: {str(e)}"
    
    return state


def escalation_node(state: GraphState) -> GraphState:
    """
    NODE 3: ESCALATION NODE
    
    Purpose: Handle queries that need human intervention
    
    How it works:
      1. Takes the query and category from state
      2. Creates an escalation message
      3. Logs the escalation reason
      4. Stores escalation message in response
      5. Returns updated state
    
    This node is triggered when:
      - Query category is uncertain
      - RAG cannot find relevant information
      - Query is complex or outside standard categories
    
    Args:
        state (GraphState): Current workflow state
        
    Returns:
        GraphState: Updated state with escalation response
    """
    
    print("\n" + "=" * 70)
    print("👤 NODE 3: ESCALATION NODE")
    print("=" * 70)
    
    query = state["query"]
    category = state["category"]
    
    print(f"📥 Query: {query}")
    print(f"📥 Category: {category}")
    
    # Create escalation message
    escalation_message = (
        "Your query has been escalated to human support. "
        "A support representative will assist you shortly. "
        "Ticket ID: SUPPORT-2026-001"
    )
    
    # Log escalation reason
    escalation_reason = f"Complex query in category: {category}"
    print(f"✅ Query Escalated")
    print(f"   Reason: {escalation_reason}")
    
    # Update state
    state["response"] = escalation_message
    state["escalation_reason"] = escalation_reason
    
    return state


# ============================================================================
# STEP 3: DEFINE CONDITIONAL EDGES (Router Logic)
# ============================================================================

def should_escalate(state: GraphState) -> str:
    """
    CONDITIONAL ROUTER: Decides which node to go to next
    
    This function acts as a "traffic director" that decides:
      - Should we call the RAG responder?
      - Should we escalate to human support?
    
    Logic:
      - If category is "product", "returns", or "general": Go to RAG responder
      - Only escalate for complex/unclear queries
    
    Args:
        state (GraphState): Current workflow state
        
    Returns:
        str: Node name to route to ("rag_responder" or "escalation")
    """
    
    category = state.get("category", "general")
    
    print(f"\n🚦 ROUTER: Checking category '{category}'")
    
    # Most queries should be handled by RAG responder
    # Only escalate if truly necessary
    if category in ["product", "returns", "general", "greeting"]:
        print(f"   → Routing to RAG RESPONDER")
        return "rag_responder"
    
    # For any other unexpected category, still try RAG first
    else:
        print(f"   → Routing to RAG RESPONDER (unknown category)")
        return "rag_responder"


# ============================================================================
# STEP 4: BUILD THE GRAPH
# ============================================================================

def build_graph():
    """
    BUILD GRAPH: Assemble all nodes and edges into a workflow
    
    This function:
      1. Creates a StateGraph with our GraphState
      2. Adds all nodes (classifier, rag_responder, escalation)
      3. Defines edges (connections between nodes)
      4. Sets conditional routing logic
      5. Compiles the graph for execution
    
    The final graph flow:
      START → classifier → (decision) → rag_responder → END
                                   OR
                               escalation → END
    
    Returns:
        CompiledGraph: Ready-to-execute workflow
    """
    
    print("\n" + "=" * 70)
    print("🏗️  BUILDING GRAPH")
    print("=" * 70)
    
    # Create a new StateGraph
    workflow = StateGraph(GraphState)
    
    print("✅ Created StateGraph with GraphState")
    
    # Add nodes to the graph
    print("\n📌 Adding nodes to graph...")
    workflow.add_node("greeting", greeting_node)
    print("   ✓ Added greeting_node")
    
    workflow.add_node("classifier", classifier_node)
    print("   ✓ Added classifier_node")
    
    workflow.add_node("rag_responder", rag_responder_node)
    print("   ✓ Added rag_responder_node")
    
    workflow.add_node("escalation", escalation_node)
    print("   ✓ Added escalation_node")
    
    # Define edges
    print("\n📌 Defining edges...")
    
    # Greeting routing function
    def route_greeting(state: GraphState):
        if state.get("is_greeting", False):
            return "end_greeting"
        return "classifier"
    
    # Start → Greeting (check)
    workflow.add_edge(START, "greeting")
    print("   ✓ START → greeting")
    
    # Greeting → (conditional) → classifier OR END
    workflow.add_conditional_edges(
        "greeting",
        route_greeting,
        {
            "classifier": "classifier",
            "end_greeting": END
        }
    )
    print("   ✓ greeting → (conditional) → classifier OR END")
    
    # Classifier → (conditional routing based on should_escalate)
    workflow.add_conditional_edges(
        "classifier",
        should_escalate,
        {
            "rag_responder": "rag_responder",
            "escalation": "escalation"
        }
    )
    print("   ✓ classifier → (conditional) → rag_responder OR escalation")
    
    # RAG Responder → End
    workflow.add_edge("rag_responder", END)
    print("   ✓ rag_responder → END")
    
    # Escalation → End
    workflow.add_edge("escalation", END)
    print("   ✓ escalation → END")
    
    # Compile the graph
    print("\n📌 Compiling graph...")
    graph = workflow.compile()
    print("✅ Graph compiled successfully!")
    
    return graph


# ============================================================================
# STEP 5: EXECUTE THE GRAPH
# ============================================================================

def process_query(query: str) -> str:
    """
    MAIN FUNCTION: Execute the workflow for a user query
    
    Steps:
      1. Build the graph
      2. Initialize state with user query
      3. Run the graph from START to END
      4. Extract and return the final response
    
    Args:
        query (str): User's question
        
    Returns:
        str: Final response from the workflow
    """
    
    print("\n\n" + "=" * 70)
    print("🚀 PROCESSING QUERY")
    print("=" * 70)
    print(f"Query: {query}")
    
    # Build the graph
    graph = build_graph()
    
    # Initialize the state
    initial_state = {
        "query": query,
        "category": "",
        "context": "",
        "response": "",
        "escalation_reason": "",
        "is_greeting": False
    }
    
    print(f"\n✅ Initial state created")
    
    # Execute the graph
    print(f"\n🔄 Executing graph...\n")
    final_state = graph.invoke(initial_state)
    
    # Extract and return the response
    response = final_state.get("response", "No response generated")
    
    print("\n" + "=" * 70)
    print("✅ WORKFLOW COMPLETE")
    print("=" * 70)
    print(f"📤 Final Response: {response}")
    
    return response


# ============================================================================
# TEST THE GRAPH
# ============================================================================

def main():
    """Test the graph with sample queries"""
    
    print("\n\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#" + " " * 15 + "🌐 LANGGRAPH WORKFLOW DEMO" + " " * 27 + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)
    
    # Test queries
    test_queries = [
        "What is the price of SmartWatch Pro X?",  # Should go to RAG (product)
        "Can I return items within 7 days?",       # Should go to RAG (returns)
        "Tell me a joke about tech",                # Should escalate (general)
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'#' * 70}")
        print(f"TEST QUERY {i}/{len(test_queries)}")
        print(f"{'#' * 70}")
        
        response = process_query(query)
        
        print(f"\n{'─' * 70}")
        print(f"Query: {query}")
        print(f"Response: {response}")
        print(f"{'─' * 70}")


if __name__ == "__main__":
    main()
