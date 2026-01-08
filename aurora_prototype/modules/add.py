from typing import Any


class AddModule:
    name = "add"
    description = "Adds two numbers."

    def run(self, params: dict[str, Any]) -> dict[str, Any]:
        try:
            a = float(params.get("a", 0))
            b = float(params.get("b", 0))
        except (TypeError, ValueError):
            raise ValueError("Both 'a' and 'b' must be numbers.")

        return {
            "module": self.name,
            "a": a,
            "b": b,
            "result": a + b,
        }
