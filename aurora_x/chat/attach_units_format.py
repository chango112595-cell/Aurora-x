# FastAPI endpoint for formatting values with units to human-friendly strings
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class UnitItem(BaseModel):
    value: float
    unit: str


class SingleFormatRequest(BaseModel):
    value: float | None = None
    unit: str | None = None
    values: list[UnitItem] | None = None


_SI = [(1e12, "T"), (1e9, "G"), (1e6, "M"), (1e3, "k"), (1.0, ""), (1e-3, "m"), (1e-6, "µ"), (1e-9, "n")]

# Simple catalog for friendly hints (expand later)
_HINTS = {
    ("m", 6.9e6, 7.9e6): "LEO-ish altitude",
    ("m", 4.0e7, 4.5e7): "GEO orbit radius scale",
    ("m", 1.495e11, 1.500e11): "1 AU (Earth-Sun distance)",
    ("m", 3.84e8, 3.85e8): "Earth-Moon distance",
    ("m/s", 7.5e3, 8.0e3): "LEO orbital speed",
    ("m/s", 2.9e4, 3.2e4): "Earth orbital speed",
    ("m/s", 2.9e8, 3.1e8): "Speed of light (≈ c)",
    ("kg", 5.9e24, 6.1e24): "Mass of Earth",
    ("kg", 1.98e30, 2.00e30): "Mass of Sun",
    ("kg", 7.34e22, 7.36e22): "Mass of Moon",
}


def _si_fmt(value: float, unit: str) -> str:
    v = float(value)
    for scale, prefix in _SI:
        if (v >= scale and scale >= 1) or (scale < 1 and v < 1 and v >= scale):
            return f"{v/scale:.3g} {prefix}{unit}".strip()
    return f"{v:.3g} {unit}"


def _hint(value: float, unit: str) -> str | None:
    for (u, lo, hi), msg in _HINTS.items():
        if unit == u and (lo <= value <= hi):
            return msg
    return None


def attach_units_format(app: FastAPI):
    @app.post("/api/format/units")
    async def api_format_units(request: SingleFormatRequest) -> dict[str, Any]:
        """
        Format values with units into human-friendly strings with SI prefixes.

        Examples:
        - {"value": 7e6, "unit": "m"} → "7 Mm (LEO-ish altitude)"
        - {"values": [{"value":7e6,"unit":"m"}, {"value":3e8,"unit":"m/s"}]}
        """
        items = []

        # Handle both single value and multiple values
        if request.values is not None and isinstance(request.values, list):
            items = [{"value": item.value, "unit": item.unit} for item in request.values]
        elif request.value is not None and request.unit is not None:
            items = [{"value": request.value, "unit": request.unit}]
        else:
            raise HTTPException(status_code=400, detail="provide {'value','unit'} or {'values': [...] }")

        out = []
        for it in items:
            try:
                v = float(it["value"])
                u = str(it["unit"]).strip()
            except Exception as e:
                raise HTTPException(
                    status_code=422, detail="invalid item; needs numeric 'value' and string 'unit'"
                ) from e

            pretty = _si_fmt(v, u)
            note = _hint(v, u)
            result = {"value": v, "unit": u, "pretty": pretty}
            if note:
                result["hint"] = note
            out.append(result)

        return {"ok": True, "items": out}
