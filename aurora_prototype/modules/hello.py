from typing import Any, Dict


class HelloModule:
    name = "hello"
    description = "Returns a greeting."

    def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        who = params.get("name") or params.get("who") or "world"
        return {
            "message": f"Hello, {who}!",
            "module": self.name,
        }
