"""
NEXUS Core - Main Entry Point
The orchestrator: boot sequence, logic gate, agentic loop.
"""

from components.boot_manager import BootTracker
from components import session_memory
from components import voice
from components import llm_provider

MODEL = "ministral-3"

BASE_PROMPT = """
You are NEXUS, an advanced AI assistant currently under development.
Neural Executive Utility System.

Core Identity:
- Efficient
- Direct
- Technically capable
- Short natural replies

Behavior Rules:
- Give concise and useful answers.
- Stay clear and structured.
- Avoid unnecessary filler.
- Be practical and solution-oriented.
- Adapt to the ongoing conversation context.
- Remember recent conversation history provided to you.
- If information is missing, ask focused questions.
- Prioritize accuracy and reasoning.
- Do not use bold text in answers.
- Do not answer like a robot.

System State:
- Running locally through Ollama
- Terminal-based interface
- Session memory enabled
- Long-term memory not fully implemented
- Tool execution currently disabled

Limitations:
- Cannot access the internet
- Cannot execute terminal commands
- Memory only lasts during the current session

You are NEXUS.
"""


def nexus_run(user_input: str) -> str:
    """Process one user turn: update memory, query LLM, store response."""
    session_memory.add_message("user", user_input)

    memory_context = session_memory.get_context()

    context = f"""{BASE_PROMPT}

Conversation History:
{memory_context}

NEXUS:"""

    response = llm_provider.ask(context, model=MODEL).strip()

    session_memory.add_message("NEXUS", response)

    return response


def nexus_loop():
    """Main terminal REPL."""
    print("--- NEXUS v0.1 Operational ---")
    print("Type 'exit' or 'quit' to shut down.\n")

    session_memory.load()

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("NEXUS: Shutting down.")
                session_memory.save()
                break

            message = nexus_run(user_input)
            print(f"NEXUS: {message}")
            clean = voice.clean_for_tts(message)
            voice.speak(clean)

        except (KeyboardInterrupt, EOFError):
            print("\nNEXUS: Shutting down.")
            session_memory.save()
            break
        except Exception as e:
            print(f"NEXUS: Internal error - {e}")


def pre_warm() -> bool:
    """Verify Ollama is installed and the model is ready before looping."""
    if not llm_provider.is_ollama_installed():
        print("NEXUS Core: Ollama is not installed. Cannot continue.")
        return False

    try:
        models = llm_provider.list_models()
        print(models)

        if MODEL not in models:
            print("NEXUS Core is missing the neuronal LLM.")
            response = input("Do you want to pull the LLM now? (yes/no): ")

            if response.strip().lower() in ("yes", "y"):
                print(f"Pulling {MODEL}...")
                if not llm_provider.pull_model(MODEL):
                    print(f"Failed to pull {MODEL}.")
                    return False
            else:
                print("NEXUS cannot start without the model.")
                return False

        return True

    except Exception as e:
        print(f"Error pre-warming {MODEL}: {e}")
        return False


def setup():
    """First-run setup process."""
    print("Initializing NEXUS for the first time...")
    print("Checking for Ollama...")

    if llm_provider.is_ollama_installed():
        print("Ollama detected.")
    else:
        print("Ollama not detected. Please install it before continuing.")
        print("Visit: https://ollama.com/download")
        return False

    print("Setup complete.")
    return True


def main():
    boot = BootTracker()
    boot_count = boot.boot()

    if boot_count == 1:
        print("NEXUS is not set up. Setting up now...")
        if not setup():
            print("Setup incomplete. Exiting.")
            return

    print("Welcome back, please wait...")
    print("NEXUS Booting...")

    if pre_warm():
        nexus_loop()
    else:
        print("NEXUS failed to boot.")


if __name__ == "__main__":
    main()
