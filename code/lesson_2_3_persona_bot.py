"""Build a persona-based business bot that uses verified business facts."""

from langchain.chat_models import init_chat_model

# Why: keep business facts in one place so prices are easy to verify.
facts = {
    "name": "Sweet Crumbs",
    "type": "Bakery",
    "city": "Lahore",
    "customers": "Students and families",
    "opening_hours": "9 AM to 9 PM",
    "prices": {
        "cupcake": 250,
        "brownie": 300,
        "chocolate cake": 1200,
        "cookie": 100,
    },
}

# Why: personas let the same bot speak differently to different customers.
personas = {
    "friendly": "Be warm, cheerful, and use simple words.",
    "formal": "Be professional, polite, and concise.",
    "sales": "Be enthusiastic and suggest one extra menu item when relevant.",
}

# Why: configuration makes the model and memory settings easy to change.
config = {
    "model": "ollama:gemma4:31b-cloud",
    "temperature": 0.2,
    "memory_size": 8,
    "default_persona": "friendly",
}


def build_system_message(persona_name):
    """Build instructions using the current facts and persona."""
    style = personas.get(
        persona_name,
        personas[config["default_persona"]],
    )

    return (
        f"You are the assistant for {facts['name']}, a {facts['type']} "
        f"in {facts['city']}. Customers: {facts['customers']}. "
        f"Opening hours: {facts['opening_hours']}. "
        f"Verified menu and prices in PKR: {facts['prices']}. "
        f"Your personality: {style} "
        "Only use these facts for business information. "
        "Never invent prices, products, or opening hours. "
        "If something is not in these facts, clearly say you do not know. "
        "Keep answers concise, around 2-3 sentences."
    )


persona_name = config["default_persona"]

messages = [
    {"role": "system", "content": build_system_message(persona_name)}
]

llm = init_chat_model(
    config["model"],
    temperature=config["temperature"],
)

print("Bot ready. Commands: /persona friendly|formal|sales, "
      "/price <item>, /add <item> <price>, /count, /reset, bye")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "bye":
        print("Bot: Goodbye!")
        break

    if user_input == "/reset":
        messages = [messages[0]]
        print("Bot: Memory cleared.")
        continue

    if user_input == "/count":
        print(f"Bot: {len(messages)} messages in memory.")
        continue

    if user_input.startswith("/persona"):
        parts = user_input.split(maxsplit=1)
        requested = parts[1].strip().lower() if len(parts) > 1 else ""

        # Why: dict.get provides a safe default for unknown persona names.
        persona_name = (
            requested
            if requested in personas
            else config["default_persona"]
        )

        messages[0]["content"] = build_system_message(persona_name)
        print(f"Bot: Style changed to: {personas[persona_name]}")
        continue

    if user_input.lower().startswith("/price"):
        parts = user_input.split(maxsplit=1)

        if len(parts) < 2 or not parts[1].strip():
            print("Bot: Please enter an item, for example /price cupcake.")
            continue

        item = parts[1].strip().lower()
        price = facts["prices"].get(item)

        # Why: prices come directly from the dictionary, not from AI guesses.
        if price is None:
            print(f"Bot: Sorry, {item} is not on our menu.")
        else:
            print(f"Bot: {item.title()} costs {price} PKR.")
        continue

    if user_input.lower().startswith("/add"):
        parts = user_input.split()

        if len(parts) < 3:
            print("Bot: Use /add item price, for example /add donut 200.")
            continue

        try:
            price = int(parts[-1])
            item = " ".join(parts[1:-1]).strip().lower()

            if not item or price < 0:
                raise ValueError

            facts["prices"][item] = price
            messages[0]["content"] = build_system_message(persona_name)
            print(f"Bot: Added {item.title()} for {price} PKR.")
        except ValueError:
            print("Bot: Please enter a valid item and non-negative whole-number price.")
        continue

    # Why: retain recent messages so the bot can use conversation context.
    messages.append({"role": "user", "content": user_input})

    response = llm.invoke(messages)

    messages.append({"role": "assistant", "content": response.text})

    messages = [messages[0]] + messages[1:][-config["memory_size"]:]

    print(f"Bot: {response.text}")