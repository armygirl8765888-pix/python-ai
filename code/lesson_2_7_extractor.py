import json
import re
import csv
from pathlib import Path
from ollama import chat

# Prices in PKR
PRICES = {
    "cupcake": 250,
    "chocolate cake": 1500,
    "brownie": 300,
    "vanilla cake": 1200,
}

# Files will be saved in the project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent
ORDERS_JSON = PROJECT_DIR / "code" / "orders.json"
ORDERS_CSV = PROJECT_DIR / "code" / "orders.csv"

MODEL = "gemma4:31b-cloud"

SYSTEM_PROMPT = """
You extract customer orders from messages.

Return ONLY one valid JSON object. Do not use Markdown fences.
Use this exact structure:
{
  "is_order": true,
  "customer_name": "Sara",
  "address": "DHA Lahore",
  "items": [
    {"name": "cupcake", "quantity": 2}
  ]
}

Rules:
- is_order must be true or false.
- If the message is only a question, is_order must be false.
- customer_name and address must be strings. Use an empty string if unknown.
- items must be a list.
- Every item must have a name and a positive integer quantity.
- Use menu item names when they clearly match the message.
- Never invent a customer name, address, item, or quantity.
- The menu is: cupcake, chocolate cake, brownie, vanilla cake.
- Do not calculate prices. Python will calculate prices.
"""

def extract_json(text):
    """Read JSON even if the model adds text around it."""
    text = text.strip()

    # First, try the entire response.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # If extra text exists, try the first JSON object.
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def extract_order(message):
    print("\nMessage:", message)

    try:
        response = chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            options={"temperature": 0},
        )
    except Exception as error:
        print("CHECK: Could not contact Ollama.")
        print("Error:", error)
        return None

    raw_text = response.message.content
    data = extract_json(raw_text)

    if data is None:
        print("CHECK: AI returned invalid JSON.")
        print("Raw AI response:", repr(raw_text))
        return None

    if not isinstance(data, dict):
        print("CHECK: JSON must be an object.")
        return None

    if not isinstance(data.get("is_order"), bool):
        print("CHECK: is_order must be true or false.")
        return None

    if not data["is_order"]:
        print("Result: This is not an order.")
        return {
            "is_order": False,
            "customer_name": "",
            "address": "",
            "items": [],
            "total": 0,
        }

    name = data.get("customer_name", "")
    address = data.get("address", "")
    items = data.get("items", [])

    if not isinstance(name, str) or not isinstance(address, str):
        print("CHECK: Customer name or address has an invalid format.")
        return None

    if not isinstance(items, list):
        print("CHECK: Items must be a list.")
        return None

    clean_items = []
    total = 0
    unknown_items = []

    for item in items:
        if not isinstance(item, dict):
            print("CHECK: An item has an invalid format.")
            return None

        item_name = item.get("name", "")
        quantity = item.get("quantity")

        if not isinstance(item_name, str):
            print("CHECK: Item name must be text.")
            return None

        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            print("CHECK: Quantity must be a positive whole number.")
            return None

        item_name = item_name.strip().lower()

        # Check the customer's message to reduce invented items.
        if item_name not in message.lower():
            print("CHECK: Item was not clearly found in the message:", item_name)
            return None

        if item_name not in PRICES:
            unknown_items.append(item_name)
            clean_items.append({
                "name": item_name,
                "quantity": quantity,
                "unit_price": None,
                "subtotal": None,
            })
            continue

        unit_price = PRICES[item_name]
        subtotal = unit_price * quantity
        total += subtotal

        clean_items.append({
            "name": item_name,
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": subtotal,
        })

    order = {
        "is_order": True,
        "customer_name": name,
        "address": address,
        "items": clean_items,
        "unknown_items": unknown_items,
        "total": total,
    }

    print("Customer:", name or "Not provided")
    print("Address:", address or "Not provided")

    for item in clean_items:
        if item["unit_price"] is None:
            print(
                f"CHECK: Unknown menu item: {item['name']} "
                "(price not calculated)"
            )
        else:
            print(
                f"{item['quantity']} x {item['name']} = "
                f"{item['subtotal']} PKR"
            )

    print("Total:", total, "PKR")
    return order


def main():
    test_messages = [
        "Hi, I need 2 cupcakes. My name is Sara, address is DHA Lahore.",
        "Salam! 2 cupcakes aur 1 chocolate cake chahiye. Ali, house 12 Gulberg",
        "1 pizza and 2 brownies, Bilal, Model Town",
        "hi do you deliver to Johar Town?",
        "Mujhe 3 brownies chahiye, naam Ahmed hai, address Garden Town.",
    ]

    orders = []

    for message in test_messages:
        order = extract_order(message)
        if order is not None and order.get("is_order") is True:
            orders.append(order)

    ORDERS_JSON.parent.mkdir(parents=True, exist_ok=True)

    with ORDERS_JSON.open("w", encoding="utf-8") as file:
        json.dump(orders, file, indent=2, ensure_ascii=False)

    csv_rows = []
    for order in orders:
        for item in order["items"]:
            csv_rows.append({
                "customer_name": order["customer_name"],
                "address": order["address"],
                "item": item["name"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
                "subtotal": item["subtotal"],
            })

    with ORDERS_CSV.open("w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "customer_name", "address", "item",
            "quantity", "unit_price", "subtotal"
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    total_value = sum(order["total"] for order in orders)

    print("\n" + "=" * 45)
    print("Orders found:", len(orders), "| Total value:", total_value, "PKR")
    print("Saved orders to:", ORDERS_JSON)
    print("Saved item rows to:", ORDERS_CSV)


if __name__ == "__main__":
    main()