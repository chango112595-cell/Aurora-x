# aurora_x/utils/units.py - Streamlined unit parsing and SI normalization

from __future__ import annotations
import re
from typing import Dict, Tuple

_LEN = {"m":1.0,"km":1e3,"cm":1e-2,"mm":1e-3,"au":1.495978707e11,"AU":1.495978707e11}
_MASS = {"kg":1.0,"g":1e-3,"tons":1e3,"ton":1e3}
_TIME = {"s":1.0,"ms":1e-3,"hours":3600,"days":86400,"years":31536000}

def normalize_value(value: float, unit: str) -> Tuple[float,str]:
    u = (unit or "").strip().lower()
    if u in _LEN:  return value*_LEN[u], "m"
    if u in _MASS: return value*_MASS[u], "kg"
    if u in _TIME: return value*_TIME[u], "s"
    # Default fallbacks for common physics
    if u == "" and value > 1e6:  # Large numbers without units likely meters
        return value, "m"
    if u == "":  # No unit specified
        return value, "kg"  # Default mass unit
    raise ValueError(f"unsupported unit: {unit}")

def normalize_payload(payload: Dict) -> Dict:
    out = {}
    for k,v in list(payload.items()):
        if isinstance(v, dict) and "value" in v and "unit" in v:
            val_si, unit_si = normalize_value(float(v["value"]), str(v["unit"]))
            out[f"{k}_{unit_si}"] = val_si
    for k,v in list(payload.items()):
        if "_" in k:
            base, unit = k.rsplit("_",1)
            try:
                val_si, unit_si = normalize_value(float(v), unit)
                out[f"{base}_{unit_si}"] = val_si
            except Exception:
                pass
    return out

_Q = re.compile(r"""
    (?P<key>[aA]|M)          # a or A (semi-major axis), or M (mass)
    \s*=\s*
    (?P<val>[-+]?\d+(?:\.\d+)?(?:e[+-]?\d+)?)
    \s*
    (?P<unit>[A-Za-z]+)?     # optional unit (km, m, kg, etc.)
""", re.I | re.X)

def extract_quantities(text: str) -> Dict[str, float]:
    """
    Parse inline quantities like: 'a=7000 km M=5.972e24 kg'
    Returns SI-normalized dict, e.g. {'a_m': 7e6, 'M_kg': 5.972e24}
    Defaults: a→meters if unit missing; M→kg if unit missing.
    """
    res: Dict[str, float] = {}
    for m in _Q.finditer(text or ""):
        key = m.group("key").lower()
        val = float(m.group("val"))
        unit = (m.group("unit") or "").lower()

        if key == "a":
            if not unit: unit = "m"
            val_si, u = normalize_value(val, unit)  # expect length unit
            res[f"a_{u}"] = val_si
        elif key == "m":
            if not unit: unit = "kg"
            val_si, u = normalize_value(val, unit)  # expect mass unit
            res[f"M_{u}"] = val_si
    return res