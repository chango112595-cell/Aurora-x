# aurora_x/utils/units.py - Streamlined unit parsing and SI normalization

from __future__ import annotations
import re
from typing import Dict, Tuple

_LEN = {"m": 1.0, "km": 1e3, "cm": 1e-2, "mm": 1e-3, "au": 1.495978707e11, "miles": 1609.344, "mile": 1609.344}
_MASS = {"kg": 1.0, "g": 1e-3, "tons": 1e3, "ton": 1e3}
_TIME = {"s": 1.0, "ms": 1e-3, "hours": 3600, "days": 86400, "years": 31536000}

def normalize_value(value: float, unit: str) -> Tuple[float, str]:
    """Convert a numeric value with a given unit to SI and return (value_si, si_unit).

    Recognizes length, mass and time units. If unit is empty, make a reasonable
    default based on the magnitude (large numbers->meters) or caller expectation.
    """
    u = (unit or "").strip().lower()
    if u in _LEN:
        return value * _LEN[u], "m"
    if u in _MASS:
        return value * _MASS[u], "kg"
    if u in _TIME:
        return value * _TIME[u], "s"

    # Default fallbacks
    if u == "" and value > 1e6:
        # Large numeric without unit: assume meters
        return value, "m"
    if u == "":
        # Default to mass if no other hint
        return value, "kg"

    raise ValueError(f"unsupported unit: {unit}")

def normalize_payload(payload: Dict) -> Dict:
    """Normalize values in a payload dictionary to SI units.

    Handles entries of the form:
      key: {"value": 7000, "unit": "km"}
    or
      key_unit: value

    Returns a new dict with keys suffixed by the SI unit (e.g. "a_m", "mass_kg").
    """
    out: Dict[str, object] = {}

    for k, v in payload.items():
        # Case: dict with explicit value/unit
        if isinstance(v, dict) and "value" in v:
            val = float(v["value"])
            unit = v.get("unit", "")
            val_si, unit_si = normalize_value(val, str(unit))
            out[f"{k}_{unit_si}"] = val_si
            continue

        # Case: key already contains a unit suffix (e.g. "a_km")
        if isinstance(k, str) and "_" in k:
            base, unit = k.rsplit("_", 1)
            try:
                val = float(v)
                val_si, unit_si = normalize_value(val, unit)
                out[f"{base}_{unit_si}"] = val_si
                continue
            except Exception:
                # fall through to copy raw value
                pass

        # Fallback: copy as-is
        out[k] = v

    return out


# Regex to extract inline quantities like: a=7000 km M=5.97e24 kg
_Q = re.compile(r"""
    (?P<key>[aAmM])       # a (semi-major axis) or m/M (mass)
    \s*=\s*
    (?P<val>[-+]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)
    \s*
    (?P<unit>[A-Za-z]+)?  # optional unit (km, m, kg, etc.)
""", re.VERBOSE)

def extract_quantities(text: str) -> Dict[str, float]:
    """Parse inline quantities and return SI-normalized dict.

    Example: 'a=7000 km M=5.972e24 kg' -> {'a_m': 7e6, 'M_kg': 5.972e24}
    If a unit is omitted, defaults are: a -> meters, M -> kilograms.
    """
    res: Dict[str, float] = {}

    for m in _Q.finditer(text or ""):
        key = (m.group("key") or "").lower()
        val = float(m.group("val"))
        unit = (m.group("unit") or "").lower()

        # Provide sensible defaults when unit omitted
        if not unit:
            unit = "m" if key == "a" else "kg" if key == "m" else ""

        if key == "a":
            val_si, u = normalize_value(val, unit)
            res[f"a_{u}"] = val_si
        elif key == "m":
            val_si, u = normalize_value(val, unit)
            # Keep mass key as uppercase 'M' in the result (historical)
            res[f"M_{u}"] = val_si

    return res