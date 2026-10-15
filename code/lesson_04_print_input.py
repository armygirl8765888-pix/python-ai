"""
This program collects business details and creates an AI prompt
to help a business explore practical AI solutions.
"""

# A personal welcome makes the tool friendlier for each business owner.
name = input("Your name: ")

# Knowing the business type helps AI suggest more relevant solutions.
business = input("Business type: ")

# A specific problem helps AI focus on a useful business improvement.
problem = input("Biggest problem: ")

# The budget helps keep the suggested solutions realistic and affordable.
budget = int(input("Monthly budget in PKR: "))

print(f"\nWelcome, {name}!")

prompt = (
    f"Suggest 3 AI solutions for a {business} that struggles with {problem}. "
    f"Budget: {budget} PKR per month."
)

print("--- Your AI Prompt ---")
print(prompt)