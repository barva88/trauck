# Minimal shim for `retell` SDK used by the project.
# This provides a Retell class with the common attributes/methods accessed by the app.
# The shim returns harmless placeholder responses and avoids making network calls.

class _ChatShim:
    def create(self, *args, **kwargs):
        return {"chat_id": "shim-chat-id", "messages": []}

    def create_completion(self, *args, **kwargs):
        return {"choices": []}

    def send_message(self, *args, **kwargs):
        return {"reply": ""}

    @property
    def sessions(self):
        class _S:
            def create(self, *a, **k):
                return {"chat_id": "shim-session-id", "messages": []}
        return _S()

    @property
    def messages(self):
        class _M:
            def create(self, *a, **k):
                return {"id": "shim-msg", "content": ""}
        return _M()


class Retell:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.chat = _ChatShim()


# Export simple constants to mimic SDK surface if imported directly
__all__ = ["Retell"]
