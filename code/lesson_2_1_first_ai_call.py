"""Create an AI tutor that explains topics at different levels."""

import time
from langchain.chat_models import init_chat_model

# Why: strip() removes extra spaces from the student's input.
topic = input("Topic: ").strip()
level = input("Level (beginner or expert): ").strip().lower()

while level not in ("beginner", "expert"):
    print("Please enter beginner or expert.")
    level = input("Level (beginner or expert): ").strip().lower()

# Why: the system message controls the tutor's role and answer length.
system_message = (
    f"You are a helpful AI tutor. The student's level is {level}. "
    "For beginners, use very easy words and a simple example. "
    "For experts, use accurate technical details. "
    "Keep the answer concise, around 3 sentences."
)

model = init_chat_model(
    "ollama:gemma4:31b-cloud",
    temperature=0.2,
)

start_time = time.perf_counter()

response = model.invoke(
    [
        ("system", system_message),
        ("human", f"Explain this topic: {topic}"),
    ]
)

elapsed = time.perf_counter() - start_time

print()
print(response.text)

usage = response.usage_metadata or {}
total_tokens = usage.get("total_tokens", "unavailable")

print()
print(f"{total_tokens} tokens in {elapsed:.1f} seconds")