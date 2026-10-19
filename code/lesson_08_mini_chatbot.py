"""Build a simple chatbot for a local business."""

# Why: These variables store the chat statistics.
message_count = 0
unanswered_count = 0
complaint_count = 0

# Why: A fixed business name makes the bot's replies consistent.
business_name = "City Care Clinic"

print(
    f"{business_name} Bot: "
    "Hi! Ask about timings, fees, location or appointments. "
    "Type 'bye' to exit."
)

# Ask the user's name only once, before the loop.
user_name = input(f"{business_name} Bot: What is your name? ").strip().title()

while True:
    user_message = input(f"{user_name}: ")
    cleaned_message = user_message.strip().lower()

    # Count every message, including bye and human handover.
    message_count += 1

    # Exit when the user types bye.
    if cleaned_message == "bye":
        print(f"{business_name} Bot: Take care, {user_name}!")
        break

    # Why: Handle complaints and human requests before other intents.
    complaint_keywords = ["complaint", "late", "problem", "unhappy"]
    human_keywords = ["human", "agent", "person"]

    if any(word in cleaned_message for word in complaint_keywords):
        complaint_count += 1
        print(
            f"{business_name} Bot: Sorry about that. "
            "The clinic manager will contact you."
        )

    elif any(word in cleaned_message for word in human_keywords):
        print(f"{business_name} Bot: Connecting you to a human...")
        break

    elif (
        cleaned_message == "hi"
        or cleaned_message.startswith("hi ")
        or cleaned_message == "hello"
        or cleaned_message.startswith("hello ")
        or cleaned_message == "salam"
    ):
        print(f"{business_name} Bot: Hello! How can I help you today?")

    elif any(word in cleaned_message for word in ["timing", "hours", "open", "close"]):
        print(
            f"{business_name} Bot: We are open 10 am to 8 pm, "
            "Monday to Saturday."
        )

    elif any(word in cleaned_message for word in ["fee", "fees", "price", "cost"]):
        print(f"{business_name} Bot: Consultation fee is 2,000 PKR.")

    elif any(word in cleaned_message for word in ["location", "address", "where"]):
        print(
            f"{business_name} Bot: We are located in Lahore. "
            "Please contact us for the exact address."
        )

    elif any(word in cleaned_message for word in ["appointment", "booking", "book"]):
        print(
            f"{business_name} Bot: Please contact the clinic "
            "to book an appointment."
        )

    else:
        unanswered_count += 1

        ai_prompt = (
            f"You are the friendly assistant of {business_name}. "
            f"Answer in 2 lines: {cleaned_message[:150]}"
        )

        print(
            f"{business_name} Bot: I am not sure yet. "
            f"In Module 2, an AI will answer: {ai_prompt}"
        )

# Print the summary after the loop ends.
print("=" * 40)
print(
    f"Chat summary: {message_count} messages, "
    f"{unanswered_count} unanswered."
)
print(f"Complaints received: {complaint_count}")