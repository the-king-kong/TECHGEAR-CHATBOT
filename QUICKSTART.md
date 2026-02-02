# 🚀 Quick Start Guide - TechGear Chatbot

## ⚡ 30-Second Setup

### **Server is already running! 🎉**

The API is live at: **http://localhost:8000**

### **Open the UI:**
Simply visit: **http://localhost:8000/**

That's it! You're done! 🎊

---

## 💬 Try These Queries

### **Test Query 1: Product Price** 
```
User: "What is the price of SmartWatch Pro X?"
Expected: "₹15,999" ✅ (from RAG)
Badge: 🛍️ Product
```

### **Test Query 2: Product Features**
```
User: "Does Wireless Earbuds have noise cancellation?"
Expected: "Yes, Wireless Earbuds Elite features ANC" ✅ (from RAG)
Badge: 🛍️ Product
```

### **Test Query 3: Return Policy**
```
User: "What is the return policy?"
Expected: "7-day no-questions-asked. Refund in 5-7 business days." ✅ (from RAG)
Badge: ↩️ Returns
```

### **Test Query 4: Battery Life**
```
User: "Battery life of power bank?"
Expected: "I don't have this information." ✅ (graceful handling)
Badge: 🛍️ Product
```

### **Test Query 5: Escalation**
```
User: "I want to speak to a human"
Expected: "Your query has been escalated to human support..." ✅ (escalation)
Badge: 👨‍💼 Escalation
```

---

## 🎨 UI Features

✅ **Soothing Colors:** Soft cyan/teal gradients  
✅ **Real-time Chat:** Instant message display  
✅ **Category Badges:** See query type (Product/Returns/Escalation)  
✅ **Loading Animation:** Visual feedback while processing  
✅ **Clear History:** Reset chat button  
✅ **Keyboard Support:** Press Enter to send  
✅ **Mobile Friendly:** Works on all devices  

---

## 🔧 Behind the Scenes

### **What Happens When You Send a Query:**

1. **Classifier Node** 🏷️
   - Analyzes query using Gemini LLM
   - Categorizes: product/returns/general

2. **Router** 🚦
   - If product/returns → RAG Responder
   - If general → Escalation Node

3. **RAG Responder Node** 🤖 (for products/returns)
   - Searches ChromaDB for matching info
   - Generates answer using Gemini LLM
   - Returns data-backed response

4. **Escalation Node** 👨‍💼 (for general)
   - Returns human support message
   - Provides ticket reference

5. **Response** 📤
   - Sent back to UI
   - Displays with category badge

---

## 📊 Database Content

Your chatbot knows about:

**Product 1: SmartWatch Pro X - ₹15,999**
- AMOLED Display (1.4")
- 5-day battery
- 50+ sports modes
- Water resistant

**Product 2: Wireless Earbuds Elite - ₹4,999**
- Active Noise Cancellation
- 24-hour total battery
- Premium sound

**Policies:**
- Returns: 7-day no-questions-asked
- Refunds: 5-7 business days
- Warranty: 1 year (Power Bank)

---

## 🔍 How Classification Works

| Query Contains | Classification | Result |
|---|---|---|
| price, cost, features, specs | **Product** | 🛍️ RAG searches database |
| return, refund, warranty, policy | **Returns** | ↩️ RAG searches database |
| human, support, agent, speak | **Escalation** | 👨‍💼 Routes to human |
| Anything else | **General** | ❓ Routes to escalation |

---

## 🌐 API Endpoints

### **User Facing:**
- `GET /` → Beautiful UI (what you see!)
- `POST /chat` → Send query (backend)

### **For Developers:**
- `GET /health` → Check if API is running
- `GET /docs` → Interactive API documentation (Swagger)
- `GET /redoc` → Alternative documentation (ReDoc)

---

## 💡 Pro Tips

1. **Ask specific questions** for better results
   - ✅ "What is the price of SmartWatch Pro X?"
   - ❌ "Tell me about stuff"

2. **Use keywords** to get routed to RAG
   - Contains "price" → Product category
   - Contains "return" → Returns category
   - Contains "human" → Escalation

3. **Watch the category badges** to understand routing
   - 🛍️ Product = Data from database (RAG)
   - ↩️ Returns = Data from database (RAG)
   - 👨‍💼 Escalation = Needs human support

4. **Clear chat** to start fresh with the `🗑️ Clear` button

---

## 🐛 Troubleshooting

**Q: "Cannot connect to the API"**
A: Check if server is running. You should see logs in the terminal.

**Q: "Getting error responses"**
A: Make sure you're connected to `http://localhost:8000` (not https)

**Q: "Category badge not showing"**
A: Refresh the page. Check browser console (F12) for errors.

**Q: "Same answer for different queries"**
A: This is expected - the database is small (2 products). As you add more products, responses will be more varied.

---

## 📚 Full Documentation

For detailed information, see:
- **TEST_GUIDE.md** → Test cases and validation
- **SYSTEM_SUMMARY.md** → Complete system architecture
- **api.py** → API code with detailed comments
- **graph.py** → Workflow logic and nodes
- **rag_chain.py** → RAG chain implementation

---

## 🎓 What You Just Built!

A production-ready RAG chatbot with:
- ✅ Intelligent query routing
- ✅ Database-backed responses
- ✅ Human escalation support
- ✅ Professional UI
- ✅ Fast API backend
- ✅ Multi-node workflow

---

## 🎉 You're All Set!

**Visit: http://localhost:8000/ and start chatting!**

---

*Built with LangChain + LangGraph + FastAPI + ChromaDB + Gemini AI*
