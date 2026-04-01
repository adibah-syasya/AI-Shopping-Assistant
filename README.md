# ShopBot 
### Your AI-Powered Personal Makeup Shopping Assistant

ShopBot is a conversational AI agent that helps customers discover makeup products, get personalised recommendations, and place orders — all through natural chat. Built to demonstrate real-world agentic AI concepts including ReAct pattern, function calling, and multi-tool orchestration.

---

## What Can ShopBot Do?

| Ask ShopBot... | What Happens |
|---|---|
| "I have acne marks, help me cover it" | Agent searches catalogue, recommends suitable products |
| "What foundations suit olive skin?" | Agent recommends with matching shades only |
| "I want the Fit Me Foundation in Natural Beige" | Agent confirms details then places the order |
| "Track my order ORD-P001-1234" | Agent retrieves order status |
| "Cancel my order" | Agent cancels and restores stock |

---

## Demo
```
You: hi, I'm Adibah
ShopBot: Hi Adibah! Welcome to our store. What are you looking for today?

You: I have an acne mark and want to cover it
ShopBot: I'd recommend our Fit Me Foundation by Maybelline (RM49.90) — 
         great for coverage. Available in Ivory 110, Natural Beige 220, 
         and Caramel 330. Which shade suits you?

You: Natural Beige 220
ShopBot: Got it! Here's your order summary:
         - Fit Me Foundation, Natural Beige 220 — RM49.90
         Shall I confirm this order, Adibah?

You: yes
ShopBot: Order confirmed! Your order ID is ORD-P001-3842. 
         Thank you for shopping with us!
```

---

## Agentic AI Concepts Demonstrated
```
User Message
     ↓
Intent Classifier        ← Is this a product query?
     ↓
Python Search Layer      ← Searches products.json
     ↓
Main Agent (ReAct Loop)  ← Reasons → Acts → Observes → Repeats
     ↓
Function Calling         ← place_order / track_order / cancel_order
     ↓
Mock Backend             ← Updates stock, saves orders
     ↓
Response to User
```

**Key concepts:**
- **ReAct Pattern** — agent reasons before acting, observes results, loops until done
- **Function Calling** — structured tool definitions via Groq API
- **Intent Classification** — LLM classifies intent before routing
- **Tool Orchestration** — multiple tools with a central dispatcher
- **State Management** — full conversation history maintained across turns
- **Anti-hallucination** — agent strictly uses catalogue data, never outside knowledge

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Core language |
| Groq (llama-3.3-70b-versatile) | LLM backbone |
| Streamlit | Chat UI |
| JSON | Lightweight product & order database |
| python-dotenv | Environment variable management |

---

## Product Catalogue

ShopBot carries products from top makeup brands:

| Brand | Products |
|---|---|
| Maybelline | Fit Me Foundation, Matte Ink Lipstick, Sky High Mascara |
| MAC | Ruby Woo Lipstick, Studio Fix Foundation |
| NYX | Soft Matte Lip Cream, Epic Ink Liner |
| Fenty Beauty | Pro Filter Foundation |

---

## Project Structure
```
shopbot/
├── knowledge_base/
│   ├── products.json        # Product catalogue with shades & stock
│   └── orders.json          # Order records (auto-generated)
├── agents/
│   └── crew.py              # Agent logic, tools, ReAct loop
├── app.py                   # Streamlit chat UI
├── .env                     # API keys (not pushed)
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.11
- Free Groq API key from [console.groq.com](https://console.groq.com)

### Installation
```bash
# Clone the repo
git clone https://github.com/adibah-syasya/AI-Shopping-Assistant.git
cd shopbot

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo GROQ_API_KEY=your_key_here > .env

# Run the app
streamlit run app.py
```

---

## About

Built by **Adibah Syasya** as a portfolio project to demonstrate agentic AI concepts in a practical, real-world use case.

Currently exploring agentic AI, RAG pipelines, and LLM applications.

LinkedIn= https://www.linkedin.com/in/adibah-syasya-0b99aa272/ 
