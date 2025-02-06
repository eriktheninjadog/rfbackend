#web_plugin.py
from flask import request, jsonify
from interaction_plugin import InteractionPlugin
from threading import Lock


class WebPlugin(InteractionPlugin):
    def __init__(self):
        self.input_buffer = []
        self.output_buffer = []
        self.lock = Lock()
        self.active_session = False

    def get_input(self, prompt: str) -> str:
        while True:
            with self.lock:
                if self.input_buffer:
                    return self.input_buffer.pop(0)

    def output_response(self, response: str) -> None:
        with self.lock:
            self.output_buffer.append(response)

    def start_session(self, initial_message: str) -> None:
        with self.lock:
            self.active_session = True
            self.output_buffer.append(initial_message)

    def exit_session(self, final_message: str) -> None:
        with self.lock:
            self.active_session = False
            self.output_buffer.append(final_message)

    def get_context(self) -> Dict[str, Any]:
        return {
            "headers": dict(request.headers),
            "remote_addr": request.remote_addr
        }

    # Flask-specific handlers
    def handle_request(self):
        if request.method == "POST":
            with self.lock:
                self.input_buffer.append(request.json.get("input", ""))
                return jsonify({"messages": self.output_buffer})
        return jsonify({"status": "active" if self.active_session else "inactive"})
