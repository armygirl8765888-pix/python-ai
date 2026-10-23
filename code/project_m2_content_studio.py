"""
AI Content Studio for Sweet Crumbs bakery in Lahore.

This studio creates menu descriptions, streams social media posts,
checks real prices, chats with customers, and reports AI usage.
"""

from langchain.chat_models import init_chat_model

# Keep model settings and memory limits together for easy changes.
config = {
    "model_name": "ollama:gemma4:31b-cloud",
    "max_messages": 10,
    "cloud_price_per_1k_tokens": 0.01,
}

facts = {
    "name": "Sweet Crumbs",
    "business_type": "Bakery",
    "city": "Lahore",
    "hours": "9 am to 10 pm",
    "delivery": "200 PKR; free for orders of 3000 PKR or more",
    "customers": "Families, students and cake lovers",
    "prices": {
        "chocolate cake": 1500,
        "cupcake": 250,
        "brownie": 300,
        "mango tart": 0,
    },
}

tones = {
    "fun": "Playful, energetic, friendly, and uses short sentences.",
    "premium": "Elegant and calm, focused on quality and freshness.",
    "urgent": "Exciting and action-focused, encouraging customers to order.",
}

# Precise answers use a low temperature to reduce creative variation.
precise = init_chat_model(
    config["model_name"],
    temperature=0.2,
)

# Creative writing uses a higher temperature for varied marketing content.
creative = init_chat_model(
    config["model_name"],
    temperature=0.8,
)

system_message = f"""
You are the customer assistant for {facts['name']}, a
{facts['business_type']} in {facts['city']}.

Business facts:
Name: {facts['name']}
City: {facts['city']}
Opening hours: {facts['hours']}
Delivery: {facts['delivery']}
Prices: {facts['prices']}
Customers: {facts['customers']}

Only use these facts when answering questions about this business.
Never invent prices, products, opening hours, ingredients, or policies.
A price of 0 means the product is coming soon and is not available yet.
If you do not know a fact, clearly say you do not know.
"""

messages = [
    {"role": "system", "content": system_message}
]

menu_count = 0
post_count = 0
price_count = 0
chat_count = 0
total_tokens = 0
total_seconds = 0.0

print("=" * 50)
print("   Sweet Crumbs AI Content Studio")
print("=" * 50)
print("Commands: /menu, /post fun|premium|urgent, /price <item>, /reset, bye")

while True:
    user_input = input("You: ").strip()

    # Empty input should not trigger an unnecessary AI call.
    if not user_input:
        print("Studio: Please enter a command or question.")
        continue

    command = user_input.lower()

    if command == "bye":
        print("Studio: Goodbye!")
        break

    elif command == "/menu":
        menu_items = []

        for item_name, item_price in facts["prices"].items():
            # Skip unavailable products before calling the AI to save tokens.
            if item_price == 0:
                print(f"Studio: Skipping {item_name} (coming soon)")
                continue

            menu_prompt = (
                f"Write exactly one attractive sentence for {item_name}, "
                f"a product at {facts['name']} in {facts['city']}. "
                "Do not invent ingredients or unsupported claims."
            )

            menu_response = creative.invoke(menu_prompt)
            description = menu_response.text

            menu_items.append({
                "name": item_name,
                "price": item_price,
                "description": description,
            })

            usage = menu_response.usage_metadata or {}
            total_tokens += usage.get("total_tokens", 0)

            timing = menu_response.response_metadata or {}
            total_seconds += timing.get("total_duration", 0) / 1_000_000_000

        print("-" * 50)

        for menu_number, menu_item in enumerate(menu_items, start=1):
            print(
                f"{menu_number}. {menu_item['name'].title()} "
                f"({menu_item['price']:,} PKR)"
            )
            print(f"   {menu_item['description']}")
            menu_count += 1

        print("-" * 50)

    elif command.startswith("/post"):
        post_parts = user_input.split(maxsplit=1)

        if len(post_parts) > 1:
            tone_name = post_parts[1].strip().lower()
        else:
            tone_name = ""

        # Unknown tone names use a default instead of causing a KeyError.
        tone_description = tones.get(
            tone_name,
            "Friendly, clear, and welcoming."
        )

        post_prompt = f"""
Write a short social media post for {facts['name']}.
Business: {facts['business_type']}
City: {facts['city']}
Opening hours: {facts['hours']}
Prices: {facts['prices']}
Delivery: {facts['delivery']}
Tone: {tone_description}

Use only the provided facts. Do not invent ingredients, discounts,
availability, or other business policies.
"""

        print(f"Studio ({tone_description}):")

        post_started = __import__("time").perf_counter()
        post_tokens = 0

        # Stream output so the user sees text as the model generates it.
        for chunk in creative.stream(post_prompt):
            if chunk.text:
                print(chunk.text, end="", flush=True)

            if chunk.usage_metadata:
                post_tokens = chunk.usage_metadata.get(
                    "total_tokens", post_tokens
                )

        print()

        post_elapsed = __import__("time").perf_counter() - post_started
        total_seconds += post_elapsed
        total_tokens += post_tokens
        post_count += 1

    elif command.startswith("/price"):
        price_parts = user_input.split(maxsplit=1)

        if len(price_parts) == 1:
            print("Studio: Please provide a product name.")
        else:
            item_name = price_parts[1].strip().lower()
            price = facts["prices"].get(item_name)

            if price is None:
                print(
                    f"Studio: {item_name.title()} is not on our menu."
                )
            elif price == 0:
                print(f"Studio: {item_name.title()} is coming soon.")
            else:
                print(
                    f"Studio: {item_name.title()} costs {price:,} PKR."
                )

            # Dictionary lookups answer prices without spending AI tokens.
            price_count += 1

    elif command == "/reset":
        # Preserve the system rules while clearing the conversation.
        messages = [
            {"role": "system", "content": system_message}
        ]
        print("Studio: Chat memory has been reset.")

    else:
        messages.append({
            "role": "user",
            "content": user_input,
        })

        # Keep the system message and the latest conversation messages.
        max_history = config["max_messages"]
        messages = [messages[0]] + messages[1:][-max_history:]

        chat_response = precise.invoke(messages)
        answer = chat_response.text

        messages.append({
            "role": "assistant",
            "content": answer,
        })

        print(f"Studio: {answer}")

        usage = chat_response.usage_metadata or {}
        sent_tokens = usage.get("input_tokens", 0)
        total_tokens += usage.get("total_tokens", 0)

        timing = chat_response.response_metadata or {}
        total_seconds += timing.get("total_duration", 0) / 1_000_000_000

        chat_count += 1

        print(
            f"        (memory: {len(messages) - 1} messages, "
            f"{sent_tokens:,} tokens sent)"
        )

# This report runs after the user types bye.
print("=" * 50)
print("Session report")
print(f"Chat answers: {chat_count}")
print(f"Menu descriptions: {menu_count}")
print(f"Posts: {post_count}")
print(f"Price answers: {price_count}")
print(
    f"AI usage: {total_tokens:,} tokens in {total_seconds:.1f} seconds"
)

estimated_cost = (
    total_tokens / 1000
) * config["cloud_price_per_1k_tokens"]

print(f"Estimated example cloud cost: ${estimated_cost:.2f}")
print("=" * 50)