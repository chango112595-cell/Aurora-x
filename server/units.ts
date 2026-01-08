/**
 * Unit conversion module for automatic normalization to SI units.
 * Supports distance, mass, time, and other common units.
 */

export interface UnitResult {
  si_value: number;
  si_unit: string | null;
  original_value: number;
  original_unit: string | null;
  conversion_factor: number;
  unit_type: string;
}

// Conversion factors to SI base units
const DISTANCE_TO_METERS: Record<string, number> = {
  // Metric
  'nm': 1e-9,      // nanometer
  'um': 1e-6,      // micrometer
  'mm': 0.001,     // millimeter
  'cm': 0.01,      // centimeter
  'dm': 0.1,       // decimeter
  'm': 1.0,        // meter (SI base)
  'km': 1000.0,    // kilometer
  'kilometers': 1000.0,
  'kilometre': 1000.0,
  'kilometres': 1000.0,

  // Imperial
  'in': 0.0254,    // inch
  'inch': 0.0254,
  'inches': 0.0254,
  'ft': 0.3048,    // foot
  'foot': 0.3048,
  'feet': 0.3048,
  'yd': 0.9144,    // yard
  'yard': 0.9144,
  'yards': 0.9144,
  'mi': 1609.344,  // mile
  'mile': 1609.344,
  'miles': 1609.344,

  // Astronomical
  'au': 149597870700.0,  // astronomical unit
  'AU': 149597870700.0,
  'ly': 9.4607e15,       // light year
  'lightyear': 9.4607e15,
  'parsec': 3.0857e16,   // parsec
  'pc': 3.0857e16,
};

const MASS_TO_KG: Record<string, number> = {
  // Metric
  'ng': 1e-12,     // nanogram
  'ug': 1e-9,      // microgram
  'mg': 1e-6,      // milligram
  'g': 0.001,      // gram
  'gram': 0.001,
  'grams': 0.001,
  'kg': 1.0,       // kilogram (SI base)
  'kilogram': 1.0,
  'kilograms': 1.0,
  't': 1000.0,     // metric ton
  'ton': 1000.0,
  'tons': 1000.0,
  'tonne': 1000.0,
  'tonnes': 1000.0,

  // Imperial
  'oz': 0.0283495, // ounce
  'ounce': 0.0283495,
  'ounces': 0.0283495,
  'lb': 0.453592,  // pound
  'lbs': 0.453592,
  'pound': 0.453592,
  'pounds': 0.453592,
  'stone': 6.35029, // stone

  // Solar masses for astronomy
  'msun': 1.989e30,  // solar mass
  'Msun': 1.989e30,
  'M_sun': 1.989e30,
  'solar_mass': 1.989e30,
};

const TIME_TO_SECONDS: Record<string, number> = {
  // Metric time
  'ns': 1e-9,      // nanosecond
  'us': 1e-6,      // microsecond
  'ms': 0.001,     // millisecond
  's': 1.0,        // second (SI base)
  'sec': 1.0,
  'second': 1.0,
  'seconds': 1.0,
  'min': 60.0,     // minute
  'minute': 60.0,
  'minutes': 60.0,
  'h': 3600.0,     // hour
  'hr': 3600.0,
  'hour': 3600.0,
  'hours': 3600.0,
  'd': 86400.0,    // day
  'day': 86400.0,
  'days': 86400.0,
  'week': 604800.0,  // week
  'weeks': 604800.0,
  'month': 2628000.0,  // approximate month (30.4 days)
  'months': 2628000.0,
  'y': 31536000.0,   // year (365 days)
  'yr': 31536000.0,
  'year': 31536000.0,
  'years': 31536000.0,
};

// Map SI unit types to their canonical representations
const SI_UNITS: Record<string, string> = {
  'distance': 'm',     // meter
  'length': 'm',
  'mass': 'kg',        // kilogram
  'time': 's',         // second
  'duration': 's',
};

export function parse_value_with_unit(text: string): [number | null, string | null] {
  /**
   * Parse a string containing a value and unit.
   *
   * Examples:
   *     "7000 km" -> [7000.0, "km"]
   *     "5.972e24 kg" -> [5.972e24, "kg"]
   *     "1AU" -> [1.0, "AU"]
   */
  // Remove extra whitespace
  const trimmed = text.trim();

  // Pattern to match number (including scientific notation) followed by optional unit
  const patterns = [
    /^([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s*([a-zA-Z_]+)?$/,  // standard notation
    /^([+-]?\d+)\s*([a-zA-Z_]+)?$/,  // integer
  ];

  for (const pattern of patterns) {
    const match = trimmed.match(pattern);
    if (match) {
      try {
        const value = parseFloat(match[1]);
        const unit = match[2] || null;
        return [value, unit];
      } catch {
        continue;
      }
    }
  }

  return [null, null];
}

export function normalize_to_si(value: number, unit: string | null, unit_type: string | null = null): UnitResult {
  /**
   * Normalize a value with unit to SI base units.
   *
   * Args:
   *     value: Numeric value
   *     unit: Unit string (e.g., "km", "miles", "kg")
   *     unit_type: Optional hint for unit type ("distance", "mass", "time")
   *
   * Returns:
   *     Object with si_value, si_unit, conversion_factor, unit_type
   */
  if (!unit) {
    return {
      si_value: value,
      si_unit: null,
      original_value: value,
      original_unit: null,
      conversion_factor: 1.0,
      unit_type: 'unknown'
    };
  }

  const unit_lower = unit.toLowerCase();

  // Try to determine unit type and convert
  if (unit_lower in DISTANCE_TO_METERS) {
    const si_value = value * DISTANCE_TO_METERS[unit_lower];
    return {
      si_value: si_value,
      si_unit: 'm',
      original_value: value,
      original_unit: unit,
      conversion_factor: DISTANCE_TO_METERS[unit_lower],
      unit_type: 'distance'
    };
  }

  if (unit_lower in MASS_TO_KG) {
    const si_value = value * MASS_TO_KG[unit_lower];
    return {
      si_value: si_value,
      si_unit: 'kg',
      original_value: value,
      original_unit: unit,
      conversion_factor: MASS_TO_KG[unit_lower],
      unit_type: 'mass'
    };
  }

  if (unit_lower in TIME_TO_SECONDS) {
    const si_value = value * TIME_TO_SECONDS[unit_lower];
    return {
      si_value: si_value,
      si_unit: 's',
      original_value: value,
      original_unit: unit,
      conversion_factor: TIME_TO_SECONDS[unit_lower],
      unit_type: 'time'
    };
  }

  // Unknown unit - return as is
  return {
    si_value: value,
    si_unit: unit,
    original_value: value,
    original_unit: unit,
    conversion_factor: 1.0,
    unit_type: 'unknown'
  };
}

export function get_canonical_unit(unit_type: string): string | null {
  /**
   * Get the canonical SI unit for a given unit type.
   *
   * Args:
   *     unit_type: Type of unit ("distance", "mass", "time", etc.)
   *
   * Returns:
   *     SI unit string or null if unknown type
   */
  return SI_UNITS[unit_type.toLowerCase()] || null;
}

export function detect_units_in_text(text: string): {
  detected_units: Array<{
    variable: string | null;
    original_value: number;
    original_unit: string;
    si_value: number;
    si_unit: string | null;
    unit_type: string;
    position: [number, number];
  }>;
  has_units: boolean;
  original_text: string;
} {
  /**
   * Detect all values with units in a text string.
   *
   * Returns an object with detected values and their units.
   */
  const detected: Array<any> = [];

  // Pattern to find variable=value unit pairs
  const pattern = /([a-zA-Z_]+\s*[=:]\s*)?([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s*([a-zA-Z_]+)/g;

  let match;
  while ((match = pattern.exec(text)) !== null) {
    const var_part = match[1] || "";
    const value_str = match[2];
    const unit = match[3];

    // Extract variable name if present
    const var_match = var_part.match(/([a-zA-Z_]+)\s*[=:]/);
    const var_name = var_match ? var_match[1] : null;

    try {
      const value = parseFloat(value_str);
      const norm = normalize_to_si(value, unit);

      detected.push({
        variable: var_name,
        original_value: value,
        original_unit: unit,
        si_value: norm.si_value,
        si_unit: norm.si_unit,
        unit_type: norm.unit_type,
        position: [match.index, match.index + match[0].length] as [number, number]
      });
    } catch {
      continue;
    }
  }

  return {
    detected_units: detected,
    has_units: detected.length > 0,
    original_text: text
  };
}
