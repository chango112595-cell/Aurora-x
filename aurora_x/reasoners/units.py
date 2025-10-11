"""
Unit conversion module for automatic normalization to SI units.
Supports distance, mass, time, and other common units.
"""

import re
from typing import Dict, Tuple, Optional, Any

# Conversion factors to SI base units
DISTANCE_TO_METERS = {
    # Metric
    'nm': 1e-9,      # nanometer
    'um': 1e-6,      # micrometer
    'mm': 0.001,     # millimeter
    'cm': 0.01,      # centimeter
    'dm': 0.1,       # decimeter
    'm': 1.0,        # meter (SI base)
    'km': 1000.0,    # kilometer
    'kilometers': 1000.0,
    'kilometre': 1000.0,
    'kilometres': 1000.0,
    
    # Imperial
    'in': 0.0254,    # inch
    'inch': 0.0254,
    'inches': 0.0254,
    'ft': 0.3048,    # foot
    'foot': 0.3048,
    'feet': 0.3048,
    'yd': 0.9144,    # yard
    'yard': 0.9144,
    'yards': 0.9144,
    'mi': 1609.344,  # mile
    'mile': 1609.344,
    'miles': 1609.344,
    
    # Astronomical
    'au': 149597870700.0,  # astronomical unit
    'AU': 149597870700.0,
    'ly': 9.4607e15,       # light year
    'lightyear': 9.4607e15,
    'parsec': 3.0857e16,   # parsec
    'pc': 3.0857e16,
}

MASS_TO_KG = {
    # Metric
    'ng': 1e-12,     # nanogram
    'ug': 1e-9,      # microgram
    'mg': 1e-6,      # milligram
    'g': 0.001,      # gram
    'gram': 0.001,
    'grams': 0.001,
    'kg': 1.0,       # kilogram (SI base)
    'kilogram': 1.0,
    'kilograms': 1.0,
    't': 1000.0,     # metric ton
    'ton': 1000.0,
    'tons': 1000.0,
    'tonne': 1000.0,
    'tonnes': 1000.0,
    
    # Imperial
    'oz': 0.0283495, # ounce
    'ounce': 0.0283495,
    'ounces': 0.0283495,
    'lb': 0.453592,  # pound
    'lbs': 0.453592,
    'pound': 0.453592,
    'pounds': 0.453592,
    'stone': 6.35029, # stone
    
    # Solar masses for astronomy
    'msun': 1.989e30,  # solar mass
    'Msun': 1.989e30,
    'M_sun': 1.989e30,
    'solar_mass': 1.989e30,
}

TIME_TO_SECONDS = {
    # Metric time
    'ns': 1e-9,      # nanosecond
    'us': 1e-6,      # microsecond
    'ms': 0.001,     # millisecond
    's': 1.0,        # second (SI base)
    'sec': 1.0,
    'second': 1.0,
    'seconds': 1.0,
    'min': 60.0,     # minute
    'minute': 60.0,
    'minutes': 60.0,
    'h': 3600.0,     # hour
    'hr': 3600.0,
    'hour': 3600.0,
    'hours': 3600.0,
    'd': 86400.0,    # day
    'day': 86400.0,
    'days': 86400.0,
    'week': 604800.0,  # week
    'weeks': 604800.0,
    'month': 2628000.0,  # approximate month (30.4 days)
    'months': 2628000.0,
    'y': 31536000.0,   # year (365 days)
    'yr': 31536000.0,
    'year': 31536000.0,
    'years': 31536000.0,
}

# Map SI unit types to their canonical representations
SI_UNITS = {
    'distance': 'm',     # meter
    'length': 'm',
    'mass': 'kg',        # kilogram  
    'time': 's',         # second
    'duration': 's',
}

def parse_value_with_unit(text: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Parse a string containing a value and unit.
    
    Examples:
        "7000 km" -> (7000.0, "km")
        "5.972e24 kg" -> (5.972e24, "kg")
        "1AU" -> (1.0, "AU")
    """
    # Remove extra whitespace and handle various formats
    text = text.strip()
    
    # Pattern to match number (including scientific notation) followed by optional unit
    patterns = [
        r'^([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s*([a-zA-Z_]+)?$',  # standard notation
        r'^([+-]?\d+)\s*([a-zA-Z_]+)?$',  # integer
    ]
    
    for pattern in patterns:
        match = re.match(pattern, text)
        if match:
            try:
                value = float(match.group(1))
                unit = match.group(2) if match.group(2) else None
                return value, unit
            except ValueError:
                continue
    
    return None, None

def normalize_to_si(value: float, unit: str, unit_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Normalize a value with unit to SI base units.
    
    Args:
        value: Numeric value
        unit: Unit string (e.g., "km", "miles", "kg")
        unit_type: Optional hint for unit type ("distance", "mass", "time")
    
    Returns:
        Dict with si_value, si_unit, conversion_factor, unit_type
    """
    if not unit:
        return {
            'si_value': value,
            'si_unit': None,
            'original_value': value,
            'original_unit': None,
            'conversion_factor': 1.0,
            'unit_type': 'unknown'
        }
    
    unit_lower = unit.lower()
    
    # Try to determine unit type and convert
    if unit_lower in DISTANCE_TO_METERS:
        si_value = value * DISTANCE_TO_METERS[unit_lower]
        return {
            'si_value': si_value,
            'si_unit': 'm',
            'original_value': value,
            'original_unit': unit,
            'conversion_factor': DISTANCE_TO_METERS[unit_lower],
            'unit_type': 'distance'
        }
    
    elif unit_lower in MASS_TO_KG:
        si_value = value * MASS_TO_KG[unit_lower]
        return {
            'si_value': si_value,
            'si_unit': 'kg',
            'original_value': value,
            'original_unit': unit,
            'conversion_factor': MASS_TO_KG[unit_lower],
            'unit_type': 'mass'
        }
    
    elif unit_lower in TIME_TO_SECONDS:
        si_value = value * TIME_TO_SECONDS[unit_lower]
        return {
            'si_value': si_value,
            'si_unit': 's',
            'original_value': value,
            'original_unit': unit,
            'conversion_factor': TIME_TO_SECONDS[unit_lower],
            'unit_type': 'time'
        }
    
    # Unknown unit - return as is
    return {
        'si_value': value,
        'si_unit': unit,
        'original_value': value,
        'original_unit': unit,
        'conversion_factor': 1.0,
        'unit_type': 'unknown'
    }

def normalize_text(text: str) -> str:
    """
    Find and normalize all values with units in a text string.
    Returns the text with all units converted to SI.
    
    Example:
        "a=7000 km, M=5.972e24 kg" -> "a=7000000 m, M=5.972e24 kg"
    """
    # Create a copy to work with
    result = text
    processed_positions = set()
    
    # Pattern to find variable=value unit pairs
    var_pattern = r'([a-zA-Z_]+)\s*[=:]\s*([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s*([a-zA-Z_]+)'
    
    # Find and replace all variable=value unit patterns
    replacements = []
    for match in re.finditer(var_pattern, text):
        var_name = match.group(1)
        value_str = match.group(2)
        unit = match.group(3)
        
        try:
            value = float(value_str)
            norm = normalize_to_si(value, unit)
            
            if norm['unit_type'] != 'unknown':
                # Build replacement string
                replacement = f"{var_name}={norm['si_value']} {norm['si_unit']}"
                replacements.append((match.span(), replacement))
                # Mark this position as processed
                processed_positions.add(match.span())
        except ValueError:
            continue
    
    # Apply replacements in reverse order to maintain positions
    for (start, end), replacement in sorted(replacements, reverse=True):
        result = result[:start] + replacement + result[end:]
    
    return result

def get_canonical_unit(unit_type: str) -> Optional[str]:
    """
    Get the canonical SI unit for a given unit type.
    
    Args:
        unit_type: Type of unit ("distance", "mass", "time", etc.)
    
    Returns:
        SI unit string or None if unknown type
    """
    return SI_UNITS.get(unit_type.lower())

def detect_units_in_text(text: str) -> Dict[str, Any]:
    """
    Detect all values with units in a text string.
    
    Returns a dict with detected values and their units.
    """
    detected = []
    
    # Pattern to find value-unit pairs
    pattern = r'([a-zA-Z_]+\s*[=:]\s*)?([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s*([a-zA-Z_]+)'
    
    for match in re.finditer(pattern, text):
        var_part = match.group(1) or ""
        value_str = match.group(2)
        unit = match.group(3)
        
        # Extract variable name if present
        var_match = re.match(r'([a-zA-Z_]+)\s*[=:]', var_part)
        var_name = var_match.group(1) if var_match else None
        
        try:
            value = float(value_str)
            norm = normalize_to_si(value, unit)
            
            detected.append({
                'variable': var_name,
                'original_value': value,
                'original_unit': unit,
                'si_value': norm['si_value'],
                'si_unit': norm['si_unit'],
                'unit_type': norm['unit_type'],
                'position': match.span()
            })
        except ValueError:
            continue
    
    return {
        'detected_units': detected,
        'has_units': len(detected) > 0,
        'original_text': text
    }