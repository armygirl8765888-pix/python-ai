"""
Saved Bot for Sweet Crumbs bakery.

This chatbot reads business facts from faq.json,
remembers conversations, and handles common errors safely.
"""

import json
from pathlib import Path

import httpx
import ollama


# Why: Paths based on this file work from different terminal folders.
BASE_DIR = Path(__file__).resolve().parent
FAQ_FILE = BASE_DIR / "faq.json"
HISTORY_FILE = BASE_DIR / "chat_history.json"
ERROR_FILE = BASE_DIR / "errors.log"

MODEL = "gemma4:31b-cloud"


def load_faq() -> dict:
    """Load business facts from faq.json."""

    try:
        with FAQ_FILE.open("r", encoding="utf-8") as file:
            facts = json.load(file)

        if not isinstance(facts, dict):
            raise ValueError("FAQ must contain a JSON object.")

        return facts

    except FileNotFoundError:
        print(
            f"Cannot start: {FAQ_FILE.name} is missing. "
            "Please create the business FAQ file."
        )
        raise SystemExit(1)

    except (json.JSONDecodeError, ValueError) as error:
        print(f"Cannot start: faq.json is invalid. {error}")
        raise SystemExit(1)


def load_history() -> list[dict]:
    """Load previous chat messages, or start a fresh chat."""

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            history = json.load(file)

        if not isinstance(history, list) or not all(
            isinstance(message, dict)
            and message.get("role") in ("user", "assistant")
            and isinstance(message.get("content"), str)
            for message in history
        ):
            raise ValueError("History has an invalid structure.")

        print(f"Loaded {len(history)} old messages.")
        return history

    except FileNotFoundError:
        # Why: A first-time user should not need to create history manually.
        return []

    except (json.JSONDecodeError, ValueError):
        print("History file was damaged. Starting a fresh chat.")
        return []


def save_history(history: list[dict]) -> None:
    """Save conversation history as readable Unicode JSON."""

    with HISTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            history,
            file,
            indent=2,
            ensure_ascii=False,
        )


def log_error(error: Exception) -> None:
    """Append a technical error to the private error log."""

    with ERROR_FILE.open("a", encoding="utf-8") as file:
        file.write(f"{type(error).__name__}: {error}\n")


def build_system_message(facts: dict) -> str:
    """Build chatbot instructions using the current business facts."""

    # Why: Reading facts at startup lets the owner update prices without changing Python.
    return (
        f"You are the friendly customer-service assistant for "
        f"{facts.get('business_name', 'this business')}.\n"
        f"Business facts:\n{json.dumps(facts, ensure_ascii=False, indent=2)}\n"
        "Answer using these facts. Never invent prices or business policies. "
        "If the answer is not in the facts, say you do not know and "
        "suggest contacting the business. Be concise and polite. "
        "Use the previous conversation to remember the customer's name."
    )


def get_ai_reply(
    system_message: str,
    history: list[dict],
) -> str:
    """Ask Ollama to answer using the system message and chat history."""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_message},
            *history,
        ],
    )

    return response.message.content


def main() -> None:
    """Run the saved chatbot until the user says bye."""

    facts = load_faq()
    system_message = build_system_message(facts)
    history = load_history()

    print("Sweet Crumbs Bot: Ask me anything. Commands: /reset, bye")

    while True:
        try:
            user_text = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye! Your chat is saved.")
            break


        if not user_text:
            continue

        if user_text.lower() == "bye":
            print("Bot: Goodbye! Your chat is saved.")
            break
        if user_text.lower() == "/export":
            transcript_file = BASE_DIR / "transcript.txt"

            with transcript_file.open("w", encoding="utf-8") as file:
                for message in history:
                    role = message["role"]
                    content = message["content"]
                    file.write(f"{role}: {content}\n")

            print("Bot: Chat exported to transcript.txt.")
            continue

        if user_text.lower() == "/reset":
            history = []
            save_history(history)
            print("Bot: Chat history cleared.")
            continue

        # Why: Add the question temporarily, so failed AI calls can be rolled back.
        history.append({"role": "user", "content": user_text})

        try:
            reply = get_ai_reply(system_message, history)

        except httpx.ConnectError as error:
            log_error(error)
            history.pop()
            save_history(history)
            print(
                "Bot: I am offline right now. "
                "Please open the Ollama app and try again."
            )
            continue

        except ollama.ResponseError as error:
            log_error(error)
            history.pop()
            save_history(history)
            print(
                "Bot: I could not process that request. "
                "Please check the AI model and try again."
            )
            continue

        except Exception as error:
            log_error(error)
            history.pop()
            save_history(history)
            print(
                "Bot: Something went wrong. "
                "Please try again later."
            )
            continue

        history.append({"role": "assistant", "content": reply})

        try:
            save_history(history)
        except OSError as error:
            log_error(error)
            print("Bot: Warning: I could not save this chat turn.")

        print("Bot:", reply)


if __name__ == "__main__":
    main()