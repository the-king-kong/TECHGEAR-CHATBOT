# 🤖 TechGear Chatbot - Testing Guide

## ✅ System is Live!

**API Server:** `http://localhost:8000`  
**UI:** `http://localhost:8000/`  
**API Docs:** `http://localhost:8000/docs`

---

## 🧪 Test Cases (Try These in the UI)

### **Test 1: Product Price Query** ✅ RAG Responder
```
User Input: "What is the price of SmartWatch Pro X?"
Expected Output: "₹15,999" (from database)
Category Badge: 🛍️ Product
```

### **Test 2: Feature Question** ✅ RAG Responder
```
User Input: "Does Wireless Earbuds have noise cancellation?"
Expected Output: "Yes, Wireless Earbuds Elite features ANC"
Category Badge: 🛍️ Product
```

### **Test 3: Battery Specs** ✅ RAG Responder
```
User Input: "What is the battery life of the power bank?"
Expected Output: "3000mAh battery with 12+ hours backup" (from database)
Category Badge: 🛍️ Product
```

### **Test 4: Return Policy** ✅ RAG Responder
```
User Input: "What is your return policy?"
Expected Output: "7-day no-questions-asked return policy" (from database)
Category Badge: ↩️ Returns
```

### **Test 5: Escalation Request** ✅ Escalation Node
```
User Input: "I want to speak to a human"
Expected Output: "Your query has been escalated to our human support team"
Category Badge: 👨‍💼 Escalation
```

### **Test 6: General Query** ✅ Escalation Node
```
User Input: "Tell me a joke"
Expected Output: "Escalated to human support" (not in database)
Category Badge: ❓ General
```

---

## 🏗️ Architecture Flow

```
User Input (UI)
     ↓
API POST /chat endpoint
     ↓
LangGraph Workflow:
  ├─→ Classifier Node: Categorizes query
  │
  ├─→ RAG Responder Node (if product/returns):
  │   ├─ Loads ChromaDB
  │   ├─ Retrieves relevant chunks
  │   └─ Generates answer using Gemini LLM
  │
  └─→ Escalation Node (if general):
      └─ Routes to human support
     ↓
Response returned to UI with Category Badge
```

---

## 🎨 UI Features

✅ **Soft color palette** - Soothing teal/cyan gradients  
✅ **Real-time message display** - Smooth animations  
✅ **Category badges** - Shows query classification  
✅ **Loading animation** - Bouncing dots while processing  
✅ **Responsive design** - Works on mobile & desktop  
✅ **Clear chat history** - Fresh start button  
✅ **Keyboard support** - Press Enter to send  
✅ **Welcome box** - Quick tips for users  

---

## 🚀 Database Content (Used by RAG)

**File:** `data/product_info.txt`

```
✨ CHUNK 1: SmartWatch Pro X - ₹15,999
- AMOLED Display (1.4 inches)
- 5-day battery life
- 50+ sports modes
- Water resistant (5ATM)
- Heart rate & SpO2 monitoring

✨ CHUNK 2: Wireless Earbuds Elite - ₹4,999
- Active Noise Cancellation (ANC)
- 24-hour battery (8hr buds + 16hr case)
- Premium sound quality
- Quick charging
- Return Policy: 7-day no-questions-asked
- Power Bank: 10,000mAh with 25W fast charging
```

---

## 🔍 Query Classification Logic

| Query Keywords | Classification | Route |
|---|---|---|
| price, cost, specs, features, battery, how much | **Product** | RAG Responder |
| return, refund, exchange, warranty | **Returns** | RAG Responder |
| human, support, agent, manager, speak to | **Escalation** | Escalation Node |
| Everything else | **General** | Escalation Node |

---

## 📊 Test Results Expected

| Test Case | Category | Source | Expected Result |
|-----------|----------|--------|-----------------|
| SmartWatch price | Product | RAG | ✅ 15999 |
| Earbuds ANC | Product | RAG | ✅ Yes, features ANC |
| Battery life | Product | RAG | ✅ Specs from database |
| Return policy | Returns | RAG | ✅ 7-day policy |
| Speak to human | Escalation | Node | ✅ Escalation message |
| Tell a joke | General | Node | ✅ Escalation message |

---

## 🛠️ Troubleshooting

**Issue:** "Cannot connect to API"
- **Solution:** Check if server is running: `http://localhost:8000/health`

**Issue:** "API key error"
- **Solution:** Environment variable not set. Restart server with:
  ```bash
  export GOOGLE_API_KEY='AIzaSyDvYG0KZ0wLQrrvhoEI-u_DKr3vsvocS2Q'
  ```

**Issue:** "ChromaDB not found"
- **Solution:** Run `python ingest.py` to initialize database

**Issue:** No category badge showing
- **Solution:** Check browser console (F12) for errors

---

## 📝 Files Overview

```
📂 teachgearbot/
├─ frontend.html          ← Beautiful UI (open in http://localhost:8000/)
├─ api.py                 ← FastAPI server with /chat endpoint
├─ graph.py               ← LangGraph workflow (classifier, RAG, escalation)
├─ rag_chain.py           ← RAG chain with retriever & Gemini LLM
├─ ingest.py              ← Data ingestion (loads data/product_info.txt)
├─ data/
│  └─ product_info.txt    ← Database source (2 chunks)
└─ chroma_db/             ← Vector database (persisted embeddings)
```

---

## 🎯 Summary

Your chatbot now has:
✅ Professional UI with soothing colors  
✅ RAG-powered intelligent responses  
✅ LangGraph workflow with classification  
✅ Query routing (product/returns → RAG, general → escalation)  
✅ Real-time category badges  
✅ Database integration with ChromaDB  
✅ FastAPI REST endpoint  

**Ready to use! Open** `http://localhost:8000/` **in your browser!**
