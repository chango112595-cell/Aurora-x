from dataclasses import dataclass
import re
from aurora_x.reasoners.units import normalize_to_si, parse_value_with_unit, detect_units_in_text

@dataclass
class DomainIntent:
    domain: str   # 'math' | 'physics' | 'astro' | 'quantum' | 'code' | 'unknown'
    task: str     # e.g., 'evaluate', 'differentiate', 'orbital_period'
    payload: dict

MATH_KEYS = ["math","algebra","calculate","equation","integrate","differentiate","derivative","simplify","evaluate"]
PHYS_KEYS = ["physics","force","velocity","acceleration","energy","electric","magnetic","em field","orbital","orbit","gravity","period"]

def normalize_units_in_text(text: str) -> str:
    """
    Helper function to normalize all units in text to SI.
    """
    # Detect all units in the text
    detection_result = detect_units_in_text(text)
    
    if not detection_result['has_units']:
        return text
    
    # Build replacement list
    result = text
    for unit_info in sorted(detection_result['detected_units'], key=lambda x: x['position'][0], reverse=True):
        # Replace with SI normalized value
        start, end = unit_info['position']
        si_str = f"{unit_info['si_value']} {unit_info['si_unit']}" if unit_info['si_unit'] else str(unit_info['si_value'])
        
        if unit_info['variable']:
            si_str = f"{unit_info['variable']}={si_str}"
        
        result = result[:start] + si_str + result[end:]
    
    return result

def classify_domain(text: str) -> DomainIntent:
    t = (text or "").lower().strip()
    original_text = text  # Keep original for unit detection
    
    if any(k in t for k in PHYS_KEYS):
        if "orbital" in t or "orbit" in t or "period" in t:
            # Extract parameters for orbital period with unit normalization
            payload = {"hint":t, "original_text": original_text}
            
            # Enhanced patterns to capture values with units
            a_patterns = [
                r'a\s*[=:]\s*([\d.e+-]+)\s*([a-zA-Z_]+)?', 
                r'semi[_\s-]*major[_\s-]*axis[_\s-]*[=:]\s*([\d.e+-]+)\s*([a-zA-Z_]+)?'
            ]
            m_patterns = [
                r'M\s*[=:]\s*([\d.e+-]+)\s*([a-zA-Z_]+)?',
                r'mass[_\s-]*central[_\s-]*[=:]\s*([\d.e+-]+)\s*([a-zA-Z_]+)?'
            ]
            
            # Extract and normalize semi-major axis
            for pattern in a_patterns:
                a_match = re.search(pattern, text, re.I)
                if a_match:
                    a_value = float(a_match.group(1))
                    a_unit = a_match.group(2) if a_match.group(2) else 'm'
                    
                    # Normalize to SI (meters)
                    norm_result = normalize_to_si(a_value, a_unit, 'distance')
                    payload["a"] = norm_result['si_value']  # Store in meters
                    payload["a_original"] = f"{a_value} {a_unit}"
                    break
            
            # Extract and normalize mass
            for pattern in m_patterns:
                m_match = re.search(pattern, text, re.I)
                if m_match:
                    m_value = float(m_match.group(1))
                    m_unit = m_match.group(2) if m_match.group(2) else 'kg'
                    
                    # Normalize to SI (kilograms)
                    norm_result = normalize_to_si(m_value, m_unit, 'mass')
                    payload["M"] = norm_result['si_value']  # Store in kg
                    payload["M_original"] = f"{m_value} {m_unit}"
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