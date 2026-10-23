"""Generate short menu descriptions for products in one batch."""

import time
from langchain.chat_models import init_chat_model

# Why: a dictionary keeps product names and prices together.
products = {
    "Chocolate Cake": 1500,
    "Cupcake": 250,
    "Brownie": 300,
    "Donut": 200,
    "Cookie": 100,
    "Old Stock": 0,
}

# Why: create the model once to avoid repeating setup for every product.
llm = init_chat_model(
    "ollama:gemma4:31b-cloud",
    temperature=0.2,
)

results = []

# Why: accumulators let us calculate the total cost across all descriptions.
total_tokens = 0
total_seconds = 0.0

for name, price in products.items():
    if price == 0:
        print(f"Skipping {name.lower()} (no price)")
        continue

    start_time = time.perf_counter()

    response = llm.invoke(
        f"Write one appealing sentence describing {name} "
        f"for a bakery menu. Do not invent ingredients or claims."
    )

    elapsed = time.perf_counter() - start_time

    usage = response.usage_metadata or {}
    tokens = usage.get("total_tokens", 0)

    total_tokens += tokens
    total_seconds += elapsed

    results.append({
        "item": name,
        "price": price,
        "text": response.text.strip(),
    })

print("=" * 40)

for number, result in enumerate(results, start=1):
    print(f"{number}. {result['item']} ({result['price']} PKR)")
    print(f"   {result['text']}")

print("=" * 40)
print(
    f"{len(results)} descriptions, "
    f"{total_tokens} tokens, {total_seconds:.1f} seconds"
)