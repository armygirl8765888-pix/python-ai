"""Sweet Crumbs AI Business Assistant - Module 2 Final Project."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from ollama import ResponseError
from pydantic import BaseModel, Field, ValidationError
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import tool
from langchain_ollama import ChatOllama


# 1. Configuration

MODEL = "gemma4:31b-cloud"
MAX_STEPS = 5

BASE_DIR = Path(__file__).resolve().parent
BUSINESS_FILE = BASE_DIR / "business.json"
ORDERS_FILE = BASE_DIR / "orders.json"
TRANSCRIPT_FILE = BASE_DIR / "transcript.json"
ERROR_LOG_FILE = BASE_DIR / "assistant_errors.log"

logging.basicConfig(
    filename=str(ERROR_LOG_FILE),
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)

STATS: dict[str, Any] = {
    "questions": 0,
    "answered": 0,
    "errors": 0,
    "imports": 0,
    "orders_placed": 0,
    "tool_counts": {
        "get_price": 0,
        "get_info": 0,
        "order_status": 0,
        "place_order": 0,
    },
}


# 2. JSON helper functions

def load_json_file(path: Path, default: Any) -> Any:
    """Load a JSON file, handling missing and damaged files."""
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        logging.exception("Could not read %s", path.name)
        print(f"Warning: Could not read {path.name}: {error}")
        return default


def save_json_file(path: Path, data: Any) -> bool:
    """Save JSON with indentation and Unicode support."""
    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        return True
    except OSError:
        logging.exception("Could not save %s", path.name)
        print(f"Error: Could not save {path.name}.")
        return False


def read_business() -> dict[str, Any]:
    """Load and validate the owner's business data."""
    if not BUSINESS_FILE.exists():
        raise FileNotFoundError("business.json is missing from the code folder.")

    data = load_json_file(BUSINESS_FILE, None)

    if not isinstance(data, dict):
        raise ValueError("business.json must contain a JSON object.")

    required = {"name", "type", "city", "hours", "delivery", "prices"}
    if not required.issubset(data):
        raise ValueError("business.json is missing required fields.")

    if not isinstance(data["prices"], dict) or not data["prices"]:
        raise ValueError("business.json must contain menu prices.")

    for item, price in data["prices"].items():
        if not isinstance(price, (int, float)) or price < 0:
            raise ValueError(f"Invalid price for {item}.")

    return data


def read_orders() -> list[dict[str, Any]]:
    """Load saved orders."""
    data = load_json_file(ORDERS_FILE, [])

    if not isinstance(data, list):
        print("Warning: orders.json must contain a list.")
        return []

    return [item for item in data if isinstance(item, dict)]


def read_transcript() -> list[dict[str, str]]:
    """Load the saved conversation transcript."""
    data = load_json_file(TRANSCRIPT_FILE, [])

    if not isinstance(data, list):
        return []

    return [
        item for item in data
        if isinstance(item, dict)
        and isinstance(item.get("role"), str)
        and isinstance(item.get("content"), str)
    ]


def save_turn(user_text: str, assistant_text: str) -> None:
    """Save a conversation turn after each response."""
    TRANSCRIPT.append({"role": "user", "content": user_text})
    TRANSCRIPT.append({"role": "assistant", "content": assistant_text})
    if not save_json_file(TRANSCRIPT_FILE, TRANSCRIPT):
        print("Warning: transcript could not be saved.")


# 3. Business helper functions

def normalize_item(item: str) -> str:
    """Normalize an item name for matching."""
    return " ".join(item.lower().strip().split())


def calculate_total(item: str, quantity: int) -> int | float:
    """Calculate a total using the owner's saved menu prices."""
    assert quantity > 0, "Quantity must be positive."

    prices = {
        normalize_item(name): price
        for name, price in BUSINESS["prices"].items()
    }
    key = normalize_item(item)

    if key not in prices:
        raise ValueError(f"Unknown menu item: {item}")

    return prices[key] * quantity


def new_order_id() -> str:
    """Create a unique order ID."""
    return f"SC-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"


def print_tool(name: str, args: dict[str, Any]) -> None:
    """Print tool usage and update its counter."""
    print(f"[tool] {name}({args})")
    STATS["tool_counts"][name] += 1


# Business data is loaded before tool registration.
BUSINESS = read_business()
ORDERS = read_orders()
TRANSCRIPT = read_transcript()

# A simple non-AI assertion test.
assert calculate_total("cupcake", 2) == 500


# 4. Tool functions

@tool(parse_docstring=True)
def get_price(item: str) -> str:
    """Get the exact price of a menu item.

    Args:
        item: Menu item name, such as cupcake or brownie.
    """
    prices = {
        normalize_item(name): price
        for name, price in BUSINESS["prices"].items()
    }
    key = normalize_item(item)

    if key not in prices:
        return (
            f"Item '{item}' not found. Available items: "
            f"{', '.join(BUSINESS['prices'].keys())}"
        )

    currency = BUSINESS.get("currency", "PKR")
    return f"{item.title()} costs {currency} {prices[key]}."


@tool(parse_docstring=True)
def get_info(topic: str) -> str:
    """Get business information such as hours, city, or delivery.

    Args:
        topic: Information requested, such as hours, opening_hours, city, or delivery.
    """
    topic = topic.lower().strip().replace("_", " ").replace("-", " ")

    aliases = {
        "opening hours": "hours",
        "opening time": "hours",
        "business hours": "hours",
        "timings": "hours",
        "time": "hours",
        "location": "city",
        "address": "city",
        "delivery information": "delivery",
        "delivery policy": "delivery",
        "delivery charges": "delivery_fee",
    }

    key = aliases.get(topic, topic)

    if key in BUSINESS:
        return f"{key}: {BUSINESS[key]}"

    return (
        f"No information for '{topic}'. "
        f"Available topics: {', '.join(BUSINESS.keys())}"
    )


@tool(parse_docstring=True)
def order_status(order_id: str) -> str:
    """Check the status of a saved order.

    Args:
        order_id: The order ID to check.
    """
    for order in ORDERS:
        if str(order.get("order_id", "")).lower() == order_id.lower().strip():
            return (
                f"Order {order_id}: "
                f"{order.get('status', 'unknown')}."
            )

    return f"Order {order_id} was not found."


@tool(parse_docstring=True)
def place_order(customer_name: str, item: str, quantity: int) -> str:
    """Create an order after asking the owner for approval.

    Args:
        customer_name: Name of the customer.
        item: Menu item requested.
        quantity: Number of items requested.
    """
    if not customer_name.strip():
        return "Order rejected: customer name is required."

    if quantity <= 0:
        return "Order rejected: quantity must be greater than zero."

    try:
        total = calculate_total(item, quantity)
    except ValueError as error:
        return str(error)

    order = {
        "order_id": new_order_id(),
        "customer_name": customer_name.strip(),
        "item": normalize_item(item),
        "quantity": quantity,
        "total": total,
        "currency": BUSINESS.get("currency", "PKR"),
        "status": "confirmed",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    print("\nOwner approval required.")
    print(f"Customer: {order['customer_name']}")
    print(f"Item: {order['item']} x {quantity}")
    print(f"Total: {order['currency']} {total}")

    approval = input("Owner, approve this order? (yes/no): ").strip().lower()

    if approval not in {"yes", "y"}:
        return "Order was not saved because owner approval was not given."

    ORDERS.append(order)
    if not save_json_file(ORDERS_FILE, ORDERS):
        ORDERS.pop()
        return "Order could not be saved. Please check file permissions."

    STATS["orders_placed"] += 1
    return f"Order saved. Order ID: {order['order_id']}. Total: {total} PKR."


TOOLS = {
    "get_price": get_price,
    "get_info": get_info,
    "order_status": order_status,
    "place_order": place_order,
}


# 5. WhatsApp order import schema

class ImportedOrder(BaseModel):
    """Structured information extracted from a WhatsApp message."""

    is_order: bool = Field(description="True only if the message requests an order.")
    customer_name: str | None = Field(description="Customer name explicitly in message.")
    item: str | None = Field(description="Menu item requested.")
    quantity: int | None = Field(description="Positive quantity requested.")
    address: str | None = Field(description="Delivery address explicitly provided.")


def import_whatsapp_message(llm: ChatOllama) -> str:
    """Extract and validate order details from a WhatsApp message."""
    message = input("Paste the WhatsApp message: ").strip()
    if not message:
        return "No message entered."

    STATS["imports"] += 1

    try:
        extractor = llm.with_structured_output(ImportedOrder, method="json_schema")
        extracted = extractor.invoke(
            [
                SystemMessage(
                    content=(
                        "Extract order details only from the provided message. "
                        "Do not invent customer names, menu items, quantities, or addresses. "
                        "If the message is not an order, set is_order=false. "
                        "If a field is absent, use null."
                    )
                ),
                HumanMessage(content=message),
            ]
        )
    except (httpx.ConnectError, ResponseError, ValidationError, ValueError) as error:
        logging.exception("WhatsApp import failed")
        STATS["errors"] += 1
        return f"Could not process the message: {error}"

    if not extracted.is_order:
        return "This does not appear to be an order. Please reply to the customer manually."

    if not extracted.customer_name or extracted.customer_name.lower() not in message.lower():
        return "CHECK: Customer name is missing or cannot be verified in the source message."

    if not extracted.item or extracted.item.lower() not in BUSINESS["prices"]:
        return "CHECK: Menu item is missing or does not exactly match the business menu."

    if not extracted.quantity or extracted.quantity <= 0:
        return "CHECK: Quantity is missing or invalid."

    try:
        total = calculate_total(extracted.item, extracted.quantity)
    except ValueError:
        return "CHECK: Menu item could not be matched to the price list."

    print("\nExtracted order:")
    print(f"Customer: {extracted.customer_name}")
    print(f"Item: {extracted.item}")
    print(f"Quantity: {extracted.quantity}")
    print(f"Total: {BUSINESS.get('currency', 'PKR')} {total}")
    print(f"Address: {extracted.address or 'CHECK: Address not provided'}")

    approval = input("Owner, save this order? (yes/no): ").strip().lower()
    if approval not in {"yes", "y"}:
        return "Imported order was not saved."

    order = {
        "order_id": new_order_id(),
        "customer_name": extracted.customer_name,
        "item": normalize_item(extracted.item),
        "quantity": extracted.quantity,
        "total": total,
        "currency": BUSINESS.get("currency", "PKR"),
        "address": extracted.address,
        "status": "confirmed",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source": "whatsapp_import",
    }

    ORDERS.append(order)
    if not save_json_file(ORDERS_FILE, ORDERS):
        ORDERS.pop()
        return "Could not save the imported order."

    STATS["orders_placed"] += 1
    return f"Imported order saved. Order ID: {order['order_id']}."


# 6. Agent loop

SYSTEM_PROMPT = f"""
You are the helpful front desk assistant for {BUSINESS['name']}, a bakery.
Use tools for exact business information, menu prices, and order status.
Opening hours are stored under the business key 'hours'.
For opening-hours questions call get_info with topic='hours'.
Never invent prices or business facts.
Before creating an order, collect the customer's name, item, and quantity.
The place_order tool asks the owner for approval before saving.
Business information: {json.dumps(BUSINESS, ensure_ascii=False)}
"""


def run_agent(llm: ChatOllama, user_text: str) -> str:
    """Run a manually controlled, bounded tool-calling loop."""
    messages: list[Any] = [
        SystemMessage(content=SYSTEM_PROMPT),
        *[
            HumanMessage(content=turn["content"])
            if turn["role"] == "user"
            else AIMessage(content=turn["content"])
            for turn in TRANSCRIPT[-8:]
        ],
        HumanMessage(content=user_text),
    ]

    llm_with_tools = llm.bind_tools(list(TOOLS.values()))

    for _ in range(MAX_STEPS):
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            answer = str(response.content)
            STATS["answered"] += 1
            return answer

        for call in response.tool_calls:
            name = call.get("name", "")
            args = call.get("args", {})
            call_id = call.get("id", "")

            if name not in TOOLS:
                result = f"Unknown tool: {name}"
            else:
                print_tool(name, args)
                try:
                    result = TOOLS[name].invoke(args)
                except (ValidationError, ValueError, TypeError) as error:
                    logging.exception("Tool validation failed")
                    STATS["errors"] += 1
                    result = f"Tool input error: {error}"
                except Exception as error:
                    logging.exception("Tool failed")
                    STATS["errors"] += 1
                    result = f"Tool failed safely: {error}"

            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=call_id,
                )
            )

    return "I reached the tool-step limit. Please try a simpler question."


def print_report() -> None:
    """Print session totals and per-tool usage."""
    print("\n--- Session Report ---")
    print(f"Questions: {STATS['questions']}")
    print(f"Answered: {STATS['answered']}")
    print(f"Errors: {STATS['errors']}")
    print(f"WhatsApp imports: {STATS['imports']}")
    print(f"Orders placed this session: {STATS['orders_placed']}")
    print(f"Orders on file: {len(ORDERS)}")
    print("Tool counts:")
    for name, count in STATS["tool_counts"].items():
        print(f"  {name}: {count}")


def main() -> None:
    """Run the interactive Sweet Crumbs assistant."""
    llm = ChatOllama(model=MODEL, temperature=0)

    print(f"\n{BUSINESS['name']} AI Business Assistant\n")
    print("Ask anything, or use: /import, /orders, /reset, bye\n")

    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_text:
            continue

        command = user_text.lower()

        if command == "bye":
            print_report()
            break

        if command == "/orders":
            print(json.dumps(ORDERS, indent=2, ensure_ascii=False))
            save_turn(user_text, "Displayed saved orders.")
            continue

        if command == "/reset":
            TRANSCRIPT.clear()
            save_json_file(TRANSCRIPT_FILE, TRANSCRIPT)
            print("Conversation transcript reset.")
            continue

        if command == "/import":
            result = import_whatsapp_message(llm)
            print(result)
            save_turn(user_text, result)
            continue

        STATS["questions"] += 1

        try:
            answer = run_agent(llm, user_text)
            print(f"Assistant: {answer}\n")
            save_turn(user_text, answer)

        except (httpx.ConnectError, ResponseError) as error:
            logging.exception("Model connection error")
            STATS["errors"] += 1
            answer = (
                "The AI model could not be reached. Check that Ollama is running "
                "and that the configured model is available."
            )
            print(f"Assistant: {answer}\n")
            save_turn(user_text, answer)

        except Exception as error:
            logging.exception("Unexpected assistant error")
            STATS["errors"] += 1
            answer = "An unexpected error occurred. Please check the error log."
            print(f"Assistant: {answer}\n")
            save_turn(user_text, answer)


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as error:
        print(f"Setup error: {error}")