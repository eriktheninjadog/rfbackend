#console_plugin.py

from interaction_plugin import InteractionPlugin

class ConsolePlugin(InteractionPlugin):
    def get_input(self, prompt: str) -> str:
        return input(prompt)

    def output_response(self, response: str) -> None:
        print(f"\n教師: {response}\n")

    def start_session(self, initial_message: str) -> None:
        print(f"教師: {initial_message}")

    def exit_session(self, final_message: str) -> None:
        print(f"教師: {final_message}")

    def get_context(self) -> Dict[str, Any]:
        return {}
