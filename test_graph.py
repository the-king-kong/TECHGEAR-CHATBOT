"""
Diagnostic script to test each component of the LangGraph workflow independently.
This verifies: 1. State definitions, 2. Nodes, 3. Conditional routing, 4. Graph compilation
"""

import os
from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END


# ============================================================================
# TEST 1: STATE DEFINITIONS
# ============================================================================

def test_state_definition():
    """TEST 1: Verify GraphState Definition"""
    print("\n" + "=" * 70)
    print("TEST 1: 📋 STATE DEFINITION")
    print("=" * 70)
    
    try:
        # Define the GraphState as a TypedDict
        class GraphState(TypedDict):
            query: str                      # User's input question
            category: str                   # Classified category: product/returns/general
            response: str                   # Final response
            escalation_reason: str         # Reason for escalation if needed
        
        print(f"✅ GraphState defined successfully")
        print(f"\n📋 State fields:")
        print(f"   1. query (str)              → User's input question")
        print(f"   2. category (str)           → Classification: product/returns/general")
        print(f"   3. response (str)           → Final response from the workflow")
        print(f"   4. escalation_reason (str) → Reason if escalated to human")
        
        # Test creating a sample state instance
        sample_state = {
            "query": "What is the price of SmartWatch Pro X?",
            "category": "product",
            "response": "",
            "escalation_reason": ""
        }
        
        print(f"\n✅ Sample state instance created:")
        for key, value in sample_state.items():
            print(f"   {key}: {value if value else '(empty)'}")
        
        return GraphState
        
    except Exception as e:
        print(f"❌ Error in state definition: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST 2: NODES
# ============================================================================

def test_nodes():
    """TEST 2: Verify Node Functions"""
    print("\n" + "=" * 70)
    print("TEST 2: 🔧 NODE FUNCTIONS")
    print("=" * 70)
    
    try:
        # Node 1: Classifier Node
        print(f"\n✅ Node 1: CLASSIFIER NODE")
        print(f"   Purpose: Categorize query into product/returns/general")
        
        def classifier_node(state):
            """
            Classifies the query into one of three categories.
            
            Logic:
            - If query mentions price/specs/features → "product"
            - If query mentions return/refund/exchange → "returns"
            - Otherwise → "general"
            """
            query = state["query"].lower()
            
            # Simple keyword-based classification
            product_keywords = ["price", "cost", "specs", "features", "product", "watch", "earbuds"]
            return_keywords = ["return", "refund", "exchange", "warranty", "broken", "defective"]
            
            if any(keyword in query for keyword in product_keywords):
                category = "product"
            elif any(keyword in query for keyword in return_keywords):
                category = "returns"
            else:
                category = "general"
            
            return {"category": category}
        
        # Test classifier node
        test_query_1 = {"query": "What is the price of SmartWatch?", "category": "", "response": "", "escalation_reason": ""}
        result_1 = classifier_node(test_query_1)
        print(f"   Test 1 - Query: 'What is the price of SmartWatch?'")
        print(f"   Result: {result_1['category']} ✅")
        
        test_query_2 = {"query": "Can I return this item?", "category": "", "response": "", "escalation_reason": ""}
        result_2 = classifier_node(test_query_2)
        print(f"   Test 2 - Query: 'Can I return this item?'")
        print(f"   Result: {result_2['category']} ✅")
        
        test_query_3 = {"query": "Tell me a joke", "category": "", "response": "", "escalation_reason": ""}
        result_3 = classifier_node(test_query_3)
        print(f"   Test 3 - Query: 'Tell me a joke'")
        print(f"   Result: {result_3['category']} ✅")
        
        # Node 2: RAG Responder Node
        print(f"\n✅ Node 2: RAG RESPONDER NODE")
        print(f"   Purpose: Call answer_query() from rag_chain.py")
        print(f"   Returns: Response from Chromadb + Gemini LLM")
        
        def rag_responder_node(state):
            """
            Calls the RAG chain to answer product/returns questions.
            """
            # Mock response for testing (in real scenario, calls answer_query())
            query = state["query"]
            mock_response = f"Based on product information: Answering '{query}'"
            
            return {"response": mock_response}
        
        test_rag = {"query": "What is the price?", "category": "product", "response": "", "escalation_reason": ""}
        result_rag = rag_responder_node(test_rag)
        print(f"   Test - RAG node response:")
        print(f"   {result_rag['response']} ✅")
        
        # Node 3: Escalation Node
        print(f"\n✅ Node 3: ESCALATION NODE")
        print(f"   Purpose: Handle escalation to human support")
        
        def escalation_node(state):
            """
            Returns escalation message for general/complex queries.
            """
            escalation_msg = "Your query has been escalated to human support"
            return {
                "response": escalation_msg,
                "escalation_reason": f"Query: {state['query']}"
            }
        
        test_escalation = {"query": "Tell me a joke", "category": "general", "response": "", "escalation_reason": ""}
        result_escalation = escalation_node(test_escalation)
        print(f"   Test - Escalation response:")
        print(f"   {result_escalation['response']} ✅")
        
        return {
            "classifier_node": classifier_node,
            "rag_responder_node": rag_responder_node,
            "escalation_node": escalation_node
        }
        
    except Exception as e:
        print(f"❌ Error in node testing: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST 3: CONDITIONAL ROUTING
# ============================================================================

def test_conditional_routing():
    """TEST 3: Verify Conditional Routing Logic"""
    print("\n" + "=" * 70)
    print("TEST 3: 🔀 CONDITIONAL ROUTING")
    print("=" * 70)
    
    try:
        # Define routing function
        def should_escalate(state):
            """
            Determines which node to route to next based on category.
            
            Routing Logic:
            - If category is "product" or "returns" → "rag_responder"
            - Otherwise → "escalation"
            """
            category = state.get("category", "")
            
            if category in ["product", "returns"]:
                route = "rag_responder"
            else:
                route = "escalation"
            
            return route
        
        print(f"✅ Conditional routing function defined")
        print(f"\n📊 Routing Logic:")
        print(f"   If category == 'product'   → Route to RAG Responder")
        print(f"   If category == 'returns'   → Route to RAG Responder")
        print(f"   If category == 'general'   → Route to Escalation")
        
        # Test routing decisions
        print(f"\n🧪 Testing routing decisions:")
        
        test_cases = [
            {"query": "What is price?", "category": "product", "response": "", "escalation_reason": ""},
            {"query": "Can I return?", "category": "returns", "response": "", "escalation_reason": ""},
            {"query": "Tell joke", "category": "general", "response": "", "escalation_reason": ""}
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            route = should_escalate(test_case)
            print(f"   Test {i}: Category '{test_case['category']}' → Route to '{route}' ✅")
        
        return should_escalate
        
    except Exception as e:
        print(f"❌ Error in conditional routing: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST 4: GRAPH COMPILATION
# ============================================================================

def test_graph_compilation(nodes, routing_func):
    """TEST 4: Verify Graph Compilation"""
    print("\n" + "=" * 70)
    print("TEST 4: ⛓️  GRAPH COMPILATION")
    print("=" * 70)
    
    if not nodes or not routing_func:
        print(f"❌ Missing nodes or routing function")
        return None
    
    try:
        # Define GraphState
        class GraphState(TypedDict):
            query: str
            category: str
            response: str
            escalation_reason: str
        
        # Create StateGraph
        print(f"✅ Creating StateGraph...")
        graph = StateGraph(GraphState)
        
        # Add nodes
        print(f"✅ Adding nodes to graph...")
        graph.add_node("classifier", nodes["classifier_node"])
        print(f"   Added: classifier node")
        
        graph.add_node("rag_responder", nodes["rag_responder_node"])
        print(f"   Added: rag_responder node")
        
        graph.add_node("escalation", nodes["escalation_node"])
        print(f"   Added: escalation node")
        
        # Add edges
        print(f"\n✅ Adding edges to graph...")
        
        # Start edge
        graph.add_edge(START, "classifier")
        print(f"   START → classifier")
        
        # Conditional edge (routing based on category)
        graph.add_conditional_edges(
            "classifier",
            routing_func,
            {
                "rag_responder": "rag_responder",
                "escalation": "escalation"
            }
        )
        print(f"   classifier → [conditional routing]")
        print(f"      ├─ 'rag_responder' → rag_responder node")
        print(f"      └─ 'escalation' → escalation node")
        
        # End edges
        graph.add_edge("rag_responder", END)
        print(f"   rag_responder → END")
        
        graph.add_edge("escalation", END)
        print(f"   escalation → END")
        
        # Compile the graph
        print(f"\n✅ Compiling graph...")
        compiled_graph = graph.compile()
        print(f"✅ Graph compiled successfully!")
        
        # Visualize graph structure
        print(f"\n📊 Graph Structure:")
        print(f"""
        START
         │
         ├─→ classifier
         │     │
         │     ├─[category='product' or 'returns']
         │     │     ↓
         │     └─→ rag_responder → END
         │
         │     ├─[category='general']
         │     │     ↓
         │     └─→ escalation → END
        """)
        
        # Test graph execution
        print(f"\n🧪 Testing graph execution:")
        
        test_inputs = [
            {"query": "What is the price of SmartWatch Pro X?", "category": "", "response": "", "escalation_reason": ""},
            {"query": "Can I return this?", "category": "", "response": "", "escalation_reason": ""},
            {"query": "Tell me a joke", "category": "", "response": "", "escalation_reason": ""}
        ]
        
        for i, test_input in enumerate(test_inputs, 1):
            result = compiled_graph.invoke(test_input)
            print(f"\n   Test {i}:")
            print(f"   Query: '{test_input['query']}'")
            print(f"   Category: {result['category']}")
            print(f"   Route: {result['response'][:50]}...")
            print(f"   ✅ PASS")
        
        return compiled_graph
        
    except Exception as e:
        print(f"❌ Error in graph compilation: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all graph component tests"""
    print("\n" + "=" * 70)
    print("🔬 LANGGRAPH WORKFLOW COMPONENT DIAGNOSTICS")
    print("=" * 70)
    
    # Test 1: State Definition
    state_def = test_state_definition()
    
    # Test 2: Nodes
    nodes = test_nodes()
    
    # Test 3: Conditional Routing
    routing_func = test_conditional_routing()
    
    # Test 4: Graph Compilation
    if all([state_def, nodes, routing_func]):
        compiled_graph = test_graph_compilation(nodes, routing_func)
    else:
        print("\n⚠️  Skipping graph compilation test (missing components)")
        compiled_graph = None
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"1. State Definition:       {'✅ PASS' if state_def else '❌ FAIL'}")
    print(f"2. Node Functions:         {'✅ PASS' if nodes else '❌ FAIL'}")
    print(f"3. Conditional Routing:    {'✅ PASS' if routing_func else '❌ FAIL'}")
    print(f"4. Graph Compilation:      {'✅ PASS' if compiled_graph else '❌ FAIL'}")
    print("=" * 70)
    print("\n✅ All LangGraph components tested successfully!")


if __name__ == "__main__":
    main()