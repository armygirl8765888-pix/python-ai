"""
AI Skills Toolkit for Sweet Crumbs bakery.

Reusable AI skills help staff perform common tasks
with consistent prompts and predictable results.
"""

from ollama import chat


# Create both models once, at the top of the file.
# Why: Reusing these models avoids creating them repeatedly.
PRECISE_MODEL = "gemma4:31b-cloud"
CREATIVE_MODEL = "gemma4:31b-cloud"


def ask_ai(
    prompt: str,
    system: str = "You are a helpful bakery marketing assistant.",
    creative_mode: bool = False,
) -> str:
    """Ask the selected AI model and return its text response."""

    model = CREATIVE_MODEL if creative_mode else PRECISE_MODEL
    temperature = 0.8 if creative_mode else 0.2

    response = chat(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": temperature},
    )

    return response.message.content


def summarize(text: str) -> str:
    """Summarize text in a few short sentences."""

    # Why: Short summaries help busy bakery staff save time.
    prompt = f"Summarize this text in 2 short sentences:\n{text}"
    return ask_ai(prompt)


def translate(text: str, language: str = "Urdu") -> str:
    """Translate text into the requested language."""

    # Why: A default language saves time when Urdu is needed.
    prompt = f"Translate this text into {language}:\n{text}"
    return ask_ai(prompt)


def reply_to_review(review: str) -> str:
    """Write a polite and professional reply to a customer review."""

    # Why: A consistent tone helps maintain the bakery's reputation.
    prompt = (
        "Write a short, polite reply to this bakery customer review. "
        "Thank the customer and address any complaint professionally. "
        f"Review: {review}"
    )
    return ask_ai(prompt, creative_mode=True)


def estimate_tokens(text: str) -> int:
    """Estimate token count using a simple word-count approximation."""

    return len(text.split())


# These tests do not call the AI.
assert estimate_tokens("") == 0
assert estimate_tokens("Your order is ready") == 4
assert estimate_tokens("Sweet chocolate cake") == 3


def main() -> None:
    """Run the menu and count how often each skill is used."""

    print("Sweet Crumbs AI Toolkit.")
    print("Commands: /summarize, /translate, /reply, bye")

    usage = {
        "summarize": 0,
        "translate": 0,
        "reply": 0,
    }

    while True:
        command = input("\nCommand: ").strip().lower()

        if command == "bye":
            break

        elif command == "/summarize":
            text = input("Text to summarize: ").strip()

            if not text:
                print("Please enter some text.")
                continue

            result = summarize(text)
            usage["summarize"] += 1
            print("AI:", result)

        elif command == "/translate":
            text = input("Text to translate: ").strip()

            if not text:
                print("Please enter some text.")
                continue

            language = input(
                "Language (Enter for Urdu): "
            ).strip()

            # An empty answer uses the default Urdu language.
            if not language:
                result = translate(text)
            else:
                result = translate(text, language)

            usage["translate"] += 1
            print("AI:", result)

        elif command == "/reply":
            review = input("Customer review: ").strip()

            if not review:
                print("Please enter a review.")
                continue

            result = reply_to_review(review)
            usage["reply"] += 1
            print("AI:", result)
            print(
                f"(review was about {estimate_tokens(review)} tokens)"
            )

        else:
            print(
                "Unknown command. Try /summarize, "
                "/translate, /reply or bye."
            )

    print("\nSkills used today:")
    for skill, count in usage.items():
        print(f"  {skill}: {count}")


if __name__ == "__main__":
    main()