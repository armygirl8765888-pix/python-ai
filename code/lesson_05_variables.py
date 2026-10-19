"""Create an AI model profile card and estimate chat cost."""

# Why: These variables store important model information.
model_name = "llama3.2"
context_window = 128000
price_per_1k_tokens = 0.5
runs_locally = True

print("--- AI Model Profile Card ---")
print(f"Model: {model_name} {type(model_name)}")
print(f"Context window: {context_window} tokens {type(context_window)}")
print(f"Price per 1K tokens: {price_per_1k_tokens} PKR {type(price_per_1k_tokens)}")
print(f"Runs locally: {runs_locally} {type(runs_locally)}")

# Why: int() converts the user's input from text into a number.
tokens_per_chat = int(input("Tokens per chat: "))

# Why: This formula estimates the cost for one chat.
estimated_cost = (tokens_per_chat / 1000) * price_per_1k_tokens

print(f"Estimated cost: {round(estimated_cost, 2)} PKR")
chats_per_day = int(input("Chats per day: "))

monthly_cost = estimated_cost * chats_per_day * 30

print(f"Estimated monthly cost: {round(monthly_cost, 2)} PKR")