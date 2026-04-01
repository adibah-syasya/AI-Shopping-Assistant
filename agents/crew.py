from dotenv import load_dotenv
load_dotenv()
import json
import os
import random
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def load_products():
    with open("knowledge_base/products.json", "r") as f:
        data = json.load(f)
    return data["products"]

def save_products(products):
    with open("knowledge_base/products.json", "w") as f:
        json.dump({"products": products}, f, indent=2)

def load_orders():
    if not os.path.exists("knowledge_base/orders.json"):
        return []
    with open("knowledge_base/orders.json", "r") as f:
        return json.load(f)

def save_orders(orders):
    with open("knowledge_base/orders.json", "w") as f:
        json.dump(orders, f, indent=2)

# --- TOOLS ---

def search_product(query: str):
    products = load_products()
    query = query.lower()
    results = []
    for product in products:
        if (query in product["name"].lower() or
            query in product["brand"].lower() or
            query in product["category"].lower() or
            any(query in shade.lower() for shade in product["shades"])):
            results.append(product)
    if not results:
        return {"found": False, "message": "No products found matching your search."}
    return {"found": True, "products": results}

def check_stock(product_id: str):
    products = load_products()
    for product in products:
        if product["id"] == product_id:
            return {
                "product_id": product_id,
                "name": product["name"],
                "brand": product["brand"],
                "stock": product["stock"],
                "available": product["stock"] > 0
            }
    return {"available": False, "message": "Product not found."}

def place_order(product_id: str, shade: str, customer_name: str):
    products = load_products()
    for i, product in enumerate(products):
        if product["id"] == product_id:
            if product["stock"] <= 0:
                return {"success": False, "message": f"Sorry, {product['name']} is out of stock."}
            products[i]["stock"] -= 1
            save_products(products)
            order_id = f"ORD-{product_id}-{random.randint(1000, 9999)}"
            orders = load_orders()
            orders.append({
                "order_id": order_id,
                "product_id": product_id,
                "product_name": product["name"],
                "brand": product["brand"],
                "shade": shade,
                "price": product["price"],
                "customer_name": customer_name,
                "status": "confirmed"
            })
            save_orders(orders)
            return {
                "success": True,
                "order_id": order_id,
                "message": f"Order confirmed! Your order ID is {order_id}. {product['name']} in {shade} — RM{product['price']}."
            }
    return {"success": False, "message": "Product not found."}

def track_order(order_id: str):
    orders = load_orders()
    for order in orders:
        if order["order_id"] == order_id:
            return {
                "found": True,
                "order_id": order_id,
                "product": order["product_name"],
                "shade": order["shade"],
                "status": order["status"],
                "customer": order["customer_name"]
            }
    return {"found": False, "message": f"No order found with ID {order_id}."}

def cancel_order(order_id: str):
    orders = load_orders()
    for i, order in enumerate(orders):
        if order["order_id"] == order_id:
            if order["status"] == "cancelled":
                return {"success": False, "message": "Order is already cancelled."}
            orders[i]["status"] = "cancelled"
            products = load_products()
            for j, product in enumerate(products):
                if product["id"] == order["product_id"]:
                    products[j]["stock"] += 1
            save_products(products)
            save_orders(orders)
            return {"success": True, "message": f"Order {order_id} has been successfully cancelled."}
    return {"success": False, "message": f"No order found with ID {order_id}."}

# --- TOOL DEFINITIONS FOR GROQ ---

tools = [
    {
        "type": "function",
        "function": {
            "name": "place_order",
            "description": "Place an order for a product after customer confirms.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"},
                    "shade": {"type": "string"},
                    "customer_name": {"type": "string"}
                },
                "required": ["product_id", "shade", "customer_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "track_order",
            "description": "Track the status of an existing order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_order",
            "description": "Cancel an existing order and restore stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"]
            }
        }
    }
]

# --- TOOL DISPATCHER ---

def dispatch_tool(tool_name: str, tool_args: dict):
    if tool_name == "place_order":
        return place_order(**tool_args)
    elif tool_name == "track_order":
        return track_order(**tool_args)
    elif tool_name == "cancel_order":
        return cancel_order(**tool_args)
    return {"error": "Unknown tool"}

# --- INTENT CLASSIFIER ---

def is_product_query(message: str):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a classifier. Reply only with 'yes' or 'no'."},
            {"role": "user", "content": f"Is this message asking about makeup products, recommendations, orders or beauty needs? Message: '{message}'"}
        ],
        temperature=0,
        max_tokens=5
    )
    answer = response.choices[0].message.content.strip().lower()
    return "yes" in answer

# --- AGENT LOOP ---

def run_agent(conversation_history: list):
    system_prompt = """You are a helpful personal shopping assistant for a makeup store.

STRICT RULES:
- Always display prices in RM (e.g. RM49.90), never use $
- When placing an order, always use the product_id from the catalogue (e.g. P001, P002) — never use the product name as the ID
- NEVER place an order unless customer explicitly confirms with "yes", "confirm" or similar
- NEVER recommend shades not listed in the catalogue
- NEVER make up product details

Your workflow:
1. Greet customers warmly
2. Recommend products and shades strictly from search results provided
3. Ask which product and shade the customer wants
4. Ask for customer name if not provided
5. Show order summary with RM price and ask "Shall I confirm this order?"
6. Only call place_order AFTER customer confirms — use the product_id field (e.g. P001)
7. Help track or cancel orders when asked

Be warm, concise and helpful."""

    last_user_message = conversation_history[-1]["content"]

    if is_product_query(last_user_message):
        search_keywords = ["foundation", "lipstick", "mascara", "liner",
                          "concealer", "face", "lips", "eyes", "cover",
                          "acne", "makeup", "skin", "shade", "brand"]

        search_results = []
        for keyword in search_keywords:
            if keyword in last_user_message.lower():
                results = search_product(keyword)
                if results.get("found"):
                    search_results.extend(results["products"])

        if not search_results:
            search_results = load_products()

        seen = []
        unique_results = []
        for p in search_results:
            if p["id"] not in seen:
                seen.append(p["id"])
                unique_results.append(p)

        search_context = f"\n\nProducts available in our catalogue:\n{json.dumps(unique_results, indent=2)}"
        augmented_message = last_user_message + search_context
    else:
        augmented_message = last_user_message

    augmented_history = conversation_history[:-1] + [
        {"role": "user", "content": augmented_message}
    ]

    messages = [{"role": "system", "content": system_prompt}] + augmented_history

    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=1024
        )

        choice = response.choices[0]

        if choice.finish_reason == "tool_calls":
            tool_calls = choice.message.tool_calls
            messages.append(choice.message)

            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                tool_result = dispatch_tool(tool_name, tool_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

        else:
            return choice.message.content