from typing import Any


class HelloModule:
    name = "hello"
    description = "Returns a greeting."

    def run(self, params: dict[str, Any]) -> dict[str, Any]:
        who = params.get("name") or params.get("who") or "world"
        return {
            "message": f"Hello, {who}!",
            "module": self.name,
        }
