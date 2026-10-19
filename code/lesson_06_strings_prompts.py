"""Clean user questions and prepare a prompt for AI."""

# Why: strip() removes extra spaces and title() cleans the name.
user_name = input("Your name: ").strip().title()

# Why: capitalize() makes the question start with a capital letter.
messy_question = input("Your question: ")
cleaned_question = messy_question.strip().capitalize()

# Count characters and estimate tokens.
character_count = len(cleaned_question)
estimated_tokens = round(character_count / 4)

# Check for Python in any combination of capital letters.
mentions_python = "python" in cleaned_question.lower()

print("=" * 40)
print(f"Cleaned question: {cleaned_question}")
print(f"Characters: {character_count}, about {estimated_tokens} tokens")
print(f"Mentions Python: {mentions_python}")
print("=" * 40)

# Why: Slicing limits the question to 150 characters.
short_question = cleaned_question[:150]

ai_prompt = f"""You are a friendly Python tutor.
Greet {user_name} by name and answer in 3 short lines.
Question: {short_question}"""

print(ai_prompt)

# Stretch task: replace a bad word before building the final prompt.
safe_question = cleaned_question.replace("stupid", "*")

safe_prompt = f"""You are a friendly Python tutor.
Greet {user_name} by name and answer in 3 short lines.
Question: {safe_question[:150]}"""

print("=" * 40)
print("Safe prompt:")
print(safe_prompt)

# Example cost: 0.5 PKR per 1K tokens.
example_price_per_1k = 0.5
estimated_cost = (estimated_tokens / 1000) * example_price_per_1k

print(f"Estimated cost: {estimated_cost:.2f} PKR")