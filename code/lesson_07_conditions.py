"""Choose an AI model based on the task type and estimate its cost."""

# Why: strip() and lower() make task input easier to compare.
task_type = input("Task (code / private / chat): ").strip().lower()

# Why: int() converts the token input from text into a number.
estimated_tokens = int(input("Estimated tokens: "))

# Choose a model and its example price for every task type.
if task_type == "private":
    model_name = "llama3.2 (local, Ollama)"
    price_per_1k = 0
elif task_type == "code":
    model_name = "claude (cloud, strong at code)"
    price_per_1k = 0.8
elif task_type == "chat":
    model_name = "gemma (cloud, budget-friendly)"
    price_per_1k = 0.2
else:
    model_name = "gemma (cloud, budget-friendly)"
    price_per_1k = 0.2
    print("Unknown task type. Using the chat model.")

# Warn the user if the request is long.
if estimated_tokens > 4000:
    print("Warning: long request, consider shortening it.")
else:
    print("Length is fine.")

# Stretch task: check paid-user status and request length.
paid_user = input("Is this a paid user? (yes/no): ").strip().lower()

if paid_user == "no" and estimated_tokens > 2000:
    print("Upgrade to send long requests.")

# Calculate the example cost.
estimated_cost = (estimated_tokens / 1000) * price_per_1k

print(f"Chosen model: {model_name}")
print(f"Estimated cost: {estimated_cost:.2f} PKR")