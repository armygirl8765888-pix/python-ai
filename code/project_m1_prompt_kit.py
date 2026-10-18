"""
This tool creates three AI prompts for small business owners.
It helps with marketing, customer service, and business growth.
"""

# Ask the user for five business details.
business_name = input("Business name: ")
business_type = input("Business type: ")
city = input("City: ")
customers = input("Main customers: ")
budget = int(input("Monthly budget (PKR): "))

# Why: A clear header makes the output easy to read.
print("\n=========================================")
print(f"   AI Prompt Kit for {business_name}")
print("=========================================")

# Why: Business details make the marketing prompt specific.
marketing_prompt = (
    f"Write a short Instagram post for {business_name}, "
    f"a {business_type} in {city}.\n"
    f"Target {customers}. Friendly tone, 1 call to action."
)

# Why: A polite tone helps create a useful customer reply.
customer_service_prompt = (
    f"You are the manager of {business_name}. "
    "Write a polite reply to a customer\n"
    "whose order arrived late. Apologise and offer a small discount."
)

# Why: The budget helps keep growth ideas affordable.
growth_prompt = (
    f"Suggest 3 low-cost AI tools a {business_type} in {city} can use\n"
    f"to attract {customers} with a budget of {budget} PKR per month."
)

print("\n[1] Marketing")
print(marketing_prompt)

print("\n-----------------------------------------")
print("[2] Customer Service")
print(customer_service_prompt)

print("\n-----------------------------------------")
print("[3] Growth")
print(growth_prompt)

print("\n=========================================")
print("Tip: Good prompts include a role, task, audience, and tone or number.")