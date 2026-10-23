"""Create a personal AI tutor that remembers recent conversation."""

from langchain.chat_models import init_chat_model

# Why: the system message tells the tutor its role and answer length.
system_message = (
    "You are a friendly personal tutor. "
    "Give clear, helpful answers in 2-3 sentences. "
    "Remember details from the conversation when they are available."
)

messages = [
    ("system", system_message)
]

# Why: questions stores only user questions for the optional stretch task.
questions = []

llm = init_chat_model(
    "ollama:gemma4:31b-cloud",
    temperature=0.2,
)

print("Tutor: Ask me anything. Commands: /reset, /count, bye")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "bye":
        print("Tutor: Goodbye!")
        print(f"You asked {len(questions)} questions.")

        if questions:
            print(f"First question: {questions[0]}")
            print(f"Last question: {questions[-1]}")

        break

    if user_input == "/reset":
        # Why: keep the system message so the tutor retains its instructions.
        messages = [messages[0]]
        print("Tutor: Memory cleared.")
        continue

    if user_input == "/count":
        print(f"Tutor: {len(messages)} messages in memory.")
        continue

    # Why: user messages are needed so the tutor can remember the conversation.
    messages.append(("human", user_input))
    questions.append(user_input)

    response = llm.invoke(messages)

    messages.append(("assistant", response.text))

    # Why: limiting history prevents the conversation from growing forever.
    messages = [messages[0]] + messages[1:][-8:]

    usage = response.usage_metadata or {}
    tokens_sent = usage.get("input_tokens", "unavailable")

    print(f"Tutor: {response.text}")
    print(f"       (tokens sent: {tokens_sent})")