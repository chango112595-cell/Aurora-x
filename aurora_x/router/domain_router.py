from dataclasses import dataclass
import re

@dataclass
class DomainIntent:
    domain: str   # 'math' | 'physics' | 'astro' | 'quantum' | 'code' | 'unknown'
    task: str     # e.g., 'evaluate', 'differentiate', 'orbital_period'
    payload: dict

MATH_KEYS = ["math","algebra","calculate","equation","integrate","differentiate","derivative","simplify","evaluate"]
PHYS_KEYS = ["physics","force","velocity","acceleration","energy","electric","magnetic","em field","orbital","orbit","gravity","period"]

def classify_domain(text: str) -> DomainIntent:
    t = (text or "").lower().strip()
    if any(k in t for k in PHYS_KEYS):
        if "orbital" in t or "orbit" in t or "period" in t:
            # Extract parameters for orbital period
            payload = {"hint":t}
            # Try to extract a and M values with various patterns
            a_patterns = [
                r'a\s*[=:]\s*([\d.e+-]+)', 
                r'semi[_\s-]*major[_\s-]*axis[_\s-]*m?\s*[=:]\s*([\d.e+-]+)'
            ]
            m_patterns = [
                r'M\s*[=:]\s*([\d.e+-]+)',
                r'mass[_\s-]*central[_\s-]*kg?\s*[=:]\s*([\d.e+-]+)'
            ]
            
            for pattern in a_patterns:
                a_match = re.search(pattern, t, re.I)
                if a_match:
                    payload["a"] = float(a_match.group(1))
                    break
            
            for pattern in m_patterns:
                m_match = re.search(pattern, t, re.I)
                if m_match:
                    payload["M"] = float(m_match.group(1))
                    break
            
            return DomainIntent("physics","orbital_period",payload)
        if "electric" in t or "magnetic" in t or "em" in t:
            return DomainIntent("physics","em_superposition",{"hint":t})
        return DomainIntent("physics","solve",{"hint":t})
    if any(k in t for k in MATH_KEYS) or re.search(r"[0-9x+\-*/()^]", t):
        if "differentiate" in t or "derivative" in t:
            return DomainIntent("math","differentiate",{"hint":t})
        if "integrate" in t:
            return DomainIntent("math","integrate",{"hint":t})
        return DomainIntent("math","evaluate",{"expr":t})
    return DomainIntent("code","specify",{"hint":t})